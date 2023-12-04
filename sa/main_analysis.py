from pathlib import Path
from pickle import load as load_pickle

from hydroshoot.architecture import load_mtg, get_leaves
from hydroshoot.constants import co2_molar_mass
from numpy import array, arctan, pi
from pandas import read_csv, concat, DataFrame

from archi_panel.utils import print_progress_bar
from config import Params, ConfigSensitivityAnalysis


def verify_identical_leaf_number(path_preprocessed_inputs: Path, combis: list):
    nb_leaves = []
    for id_combi, *_ in combis[: 10]:
        pth = path_preprocessed_inputs / f'combi_{id_combi}'
        g, _ = load_mtg(path_mtg=str(pth / 'initial_mtg.pckl'), path_geometry=str(pth / 'geometry.bgeom'))
        nb_leaves.append(len(get_leaves(g)))
    print(set(nb_leaves))

    pass


def concat_time_series(path_outputs: Path, sky_cond: str, params: Params):
    dfs = []
    nb_combis = len(params.combinations)
    for i, combi in enumerate(params.combinations):
        id_combi, internode_scale, limb_inclination, midrib_length = combi
        print_progress_bar(iteration=i, total=nb_combis)
        df = read_csv(path_outputs / f'{sky_cond}/combi_{id_combi}/time_series.csv', sep=';', decimal='.')
        df.loc[:, 'combi'] = id_combi
        df.loc[:, 'len'] = internode_scale * params._reference_internode_length
        df.loc[:, 'r'] = limb_inclination
        df.loc[:, 'la'] = params.calc_leaf_area(midrib_length=midrib_length)
        dfs.append(df)

    res = concat(dfs)
    res.rename(columns={'Unnamed: 0': 'time'}, inplace=True)
    res['An'] *= (co2_molar_mass * 1.e-6 * 3600.)
    res.to_csv(path_outputs / f'{sky_cond}/time_series_all.csv', index=False, sep=';', decimal='.')

    pass


def concat_leaf_props(path_outputs: Path, sky_cond_infos: tuple, combinations: list) -> None:
    sky_cond, date_sim = sky_cond_infos
    prop_names = ('TopPosition', 'BotPosition', 'Length', 'Na', 'ff_sky', 'ff_leaves', 'ff_soil', 'Flux', 'Vcm25',
                  'Jm25', 'TPU25', 'Rd', 'u', 'Eabs', 'psi_head', 'gbH', 'Tlc', 'An', 'gs', 'gb', 'E', 'leaf_area')
    nb_combis = len(combinations)

    for hour in range(24):
        dfs = []
        for i, combi in enumerate(combinations):
            id_combi = combi[0]

            pth = path_outputs / f'{sky_cond}/combi_{id_combi}' / f"mtg{date_sim.replace('-', '')}{hour:02}0000.pckl"
            with open(pth, mode='rb') as f:
                g, _ = load_pickle(f)
            ids_leaf = get_leaves(g)
            props = {'leaf_id': ids_leaf}

            for s in prop_names:
                props.update({s: [g.property(s)[i] for i in ids_leaf]})

            df = DataFrame(props)
            df.loc[:, 'combi'] = id_combi
            dfs.append(df)

            print_progress_bar(iteration=i, total=nb_combis)

        res = concat(dfs)
        res.rename(columns={'Unnamed: 0': 'time'}, inplace=True)
        res.to_csv(path_outputs / f'{sky_cond}/summary_props_{hour:02}h.csv', index=False, sep=';', decimal='.')

    pass


def calc_azimuth(path_preprocessed_outputs: Path):
    azimuth = []
    for pth in path_preprocessed_outputs.iterdir():
        with open(pth / 'initial_mtg.pckl', mode='rb') as f:
            g, _ = load_pickle(f)
        azimuth += [get_azimuth(g.node(v)) for v in get_leaves(g)]
    DataFrame({"azimuth": azimuth}).to_csv(path_preprocessed_outputs.parent / 'azimuth.csv')
    pass


def get_azimuth(node):
    dx, dy, dz = array(node.TopPosition) - array(node.BotPosition)
    if dx > 0:  # heads south
        if dy > 0:  # heads east
            azi = 180 - arctan(dy / dx) / pi * 180
        else:
            azi = - (180 + arctan(dy / dx) / pi * 180)
    else:
        azi = -arctan(dy / dx) / pi * 180
    return azi


if __name__ == '__main__':
    params_sim = Params(is_include_real_panel_data=True)
    cfg = ConfigSensitivityAnalysis(is_on_remote=True)
    # verify_identical_leaf_number(path_preprocessed_inputs=cfg.path_preprocessed_inputs, combis=params.combinations)
    calc_azimuth(path_preprocessed_outputs=cfg.path_preprocessed_inputs)
    for is_hydraulic in (True, False):
        path_outputs = cfg.path_outputs.parent / "_".join(
            (cfg.path_outputs.name, f"{'psi' if is_hydraulic else 'vpd'}"))
        for sky_condition in cfg.dates:
            concat_time_series(path_outputs=path_outputs, sky_cond=sky_condition[0], params=params_sim)
            concat_leaf_props(
                path_outputs=path_outputs, sky_cond_infos=sky_condition, combinations=params_sim.combinations)

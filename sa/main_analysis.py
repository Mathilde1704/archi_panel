from pathlib import Path
from pickle import load as load_pickle

from hydroshoot.architecture import load_mtg, get_leaves
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
    for combi in params.combinations:
        id_combi, internode_scale, limb_inclination, midrib_length = combi
        df = read_csv(path_outputs / f'{sky_cond}/combi_{id_combi}/time_series.csv', sep=';', decimal='.')
        df.loc[:, 'combi'] = id_combi
        df.loc[:, 'len'] = params.internode_length.bins[list(params.internode_scale.bins).index(internode_scale)]
        df.loc[:, 'r'] = limb_inclination
        df.loc[:, 'la'] = params.leaf_area.bins[list(params.midrib_length.bins).index(midrib_length)]
        dfs.append(df)

    res = concat(dfs)
    res.rename(columns={'Unnamed: 0': 'time'}, inplace=True)
    res.to_csv(path_outputs / f'{sky_cond}/time_series_all.csv', index=False, sep=';', decimal='.')

    pass


def concat_leaf_props(path_outputs: Path, sky_cond: str, combinations: list) -> None:
    prop_names = ('TopPosition', 'BotPosition', 'Length', 'Na', 'ff_sky', 'ff_leaves', 'ff_soil', 'Flux', 'Vcm25',
                  'Jm25', 'TPU25', 'Rd', 'u', 'Eabs', 'psi_head', 'gbH', 'Tlc', 'An', 'gs', 'gb', 'E', 'leaf_area')
    nb_combis = len(combinations)

    counter = 0
    dfs = []
    for combi in combinations:
        id_combi = combi[0]
        paths_mtgs = [pth for pth in (path_outputs / f'{sky_cond}/combi_{id_combi}').iterdir()
                      if pth.stem != 'time_series']

        for pth in paths_mtgs:
            counter += 1
            with open(pth, mode='rb') as f:
                g, _ = load_pickle(f)
            ids = get_leaves(g)
            props = {'leaf_id': ids}

            for s in prop_names:
                props.update({s: [g.property(s)[i] for i in ids]})

            df = DataFrame(props)
            df.loc[:, 'combi'] = id_combi
            dfs.append(df)

            print_progress_bar(iteration=counter, total=nb_combis)

    res = concat(dfs)
    res.rename(columns={'Unnamed: 0': 'time'}, inplace=True)
    res.to_csv(path_outputs / f'{sky_cond}/summary_props.csv', index=False, sep=';', decimal='.')

    pass


if __name__ == '__main__':
    params = Params()
    path_preprocessed_date = params
    cfg = ConfigSensitivityAnalysis(is_on_remote=True)
    # verify_identical_leaf_number(path_preprocessed_inputs=cfg.path_preprocessed_inputs, combis=params.combinations)
    concat_time_series(path_outputs=cfg.path_outputs, sky_cond='clear_sky', params=params)
    concat_leaf_props(path_outputs=cfg.path_outputs, sky_cond='clear_sky', combinations=params.combinations)

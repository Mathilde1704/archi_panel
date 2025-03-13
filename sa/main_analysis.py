from datetime import datetime
from itertools import product
from pathlib import Path
from pickle import load as load_pickle

from hydroshoot.architecture import load_mtg, get_leaves
from hydroshoot.constants import co2_molar_mass
from hydroshoot.display import visu
from openalea.plantgl.all import Scene
from pandas import read_csv, concat, DataFrame, date_range

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


def concat_time_series(path_outputs: Path, scenario_weather_soil: str, params: Params):
    dfs = []
    nb_combis = len(params.combinations)
    for i, combi in enumerate(params.combinations):
        id_combi, internode_scale, limb_inclination, midrib_length = combi
        print_progress_bar(iteration=i, total=nb_combis)
        df = read_csv(path_outputs / f'{scenario_weather_soil}/combi_{id_combi}/time_series.csv', sep=';', decimal='.')
        df.loc[:, 'combi'] = id_combi
        df.loc[:, 'len'] = internode_scale * params._reference_internode_length
        df.loc[:, 'r'] = limb_inclination
        df.loc[:, 'la'] = params.calc_leaf_area(midrib_length=midrib_length)
        dfs.append(df)

    res = concat(dfs)
    res.rename(columns={'Unnamed: 0': 'time'}, inplace=True)
    res['An'] *= (co2_molar_mass * 1.e-6 * 3600.)
    res.to_csv(path_outputs / f'{scenario_weather_soil}/time_series_all.csv', index=False, sep=';', decimal='.')

    pass


def concat_leaf_props(path_sim_outputs: Path, weather_soil_scenario: str, combinations: list,
                      date_beg: str, date_end: str) -> None:
    prop_names = ('TopPosition', 'BotPosition', 'Length', 'Na', 'ff_sky', 'ff_leaves', 'ff_soil', 'Flux', 'Vcm25',
                  'Jm25', 'TPU25', 'Rd', 'u', 'Eabs', 'psi_head', 'gbH', 'Tlc', 'An', 'gs', 'gb', 'E', 'leaf_area')
    nb_combis = len(combinations)

    for dt_sim in date_range(start=datetime.strptime(date_beg, '%Y-%m-%d %H:%M:%S'),
                             end=datetime.strptime(date_end, '%Y-%m-%d %H:%M:%S'),
                             freq='H'):
        dfs = []
        for i, combi in enumerate(combinations):
            id_combi = combi[0]

            pth = path_sim_outputs / f'{weather_soil_scenario}/combi_{id_combi}' / (
                f"mtg{dt_sim.strftime('%Y%m%d%H%M%S')}.pckl")

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
        res.to_csv(path_sim_outputs / f"{weather_soil_scenario}/summary_props_{dt_sim.strftime('%y%m%d%H')}.csv",
                   index=False, sep=';', decimal='.')

    pass


def visualize_mockup(
        path_root: Path,
        combi: str,
        scenario: str,
        hour: int,
        prop: str,
        prop_limits: list) -> None:
    pth = path_root / r'preprocessed_inputs' / combi
    g_init, _ = load_mtg(path_mtg=str(pth / 'initial_mtg.pckl'), path_geometry=str(pth / 'geometry.bgeom'))
    geom = {k: v for k, v in g_init.property('geometry').items() if not g_init.node(k).label.startswith('L')}
    g_init.properties()['geometry'] = geom

    pth2 = path_root / r'outputs_psi' / scenario / combi
    g_processed, _ = load_mtg(path_mtg=str(pth2 / f'mtg20190628{hour:02d}0000.pckl'),
                              path_geometry=str(pth / 'geometry.bgeom'))
    for i, v in enumerate(prop_limits):
        g_processed.properties()['label'].update({i: 'Toto'})
        g_processed.properties()['Tlc'].update({i: v})

    mtg_scene = visu(g_processed, plot_prop=prop, scene=Scene(), view_result=True)
    mtg_scene = visu(g_init, def_elmnt_color_dict=True, scene=mtg_scene, view_result=True)

    return mtg_scene


if __name__ == '__main__':
    params_sim = Params(is_include_real_panel_data=True)
    cfg = ConfigSensitivityAnalysis(is_on_remote=False)
    # verify_identical_leaf_number(path_preprocessed_inputs=cfg.path_preprocessed_inputs, combis=params.combinations)
    for is_hydraulic in (True,):
        path_outputs = cfg.path_outputs.parent / "_".join((cfg.path_outputs.name,
                                                           f"{'psi' if is_hydraulic else 'vpd'}"))
        for (scenario_weather, _), (scenario_soil, _) in product(
                cfg.scenarios_weather, cfg.scenarios_soil_water_deficit):
            scenario_weather_soil = f'{scenario_weather}_{scenario_soil}'
            concat_time_series(
                path_outputs=path_outputs,
                scenario_weather_soil=scenario_weather_soil,
                params=params_sim)

            concat_leaf_props(
                path_sim_outputs=path_outputs,
                weather_soil_scenario=scenario_weather_soil,
                combinations=params_sim.combinations,
                date_beg=cfg.params['simulation']['sdate'],
                date_end=cfg.params['simulation']['edate'])

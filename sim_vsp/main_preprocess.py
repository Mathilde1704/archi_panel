from datetime import datetime
from itertools import product
from json import dump
from multiprocessing import Pool
from pathlib import Path
from typing import Iterable, Callable

from hydroshoot import architecture, display, io, initialisation
from openalea.mtg import traversal
from openalea.plantgl.all import Scene
from pandas import read_csv

from config import ConfigSimVSP


def build_mtg(path_digit: Path, a_L: float, b_L: float, leaf_inc: float, lim_max: float) -> tuple:
    mtg_vine = architecture.vine_mtg(path_digit)

    for v in traversal.iter_mtg2(mtg_vine, mtg_vine.root):
        architecture.vine_phyto_modular(mtg_vine, v)
        architecture.vine_axeII(mtg_vine, v, a_L=a_L, b_L=b_L, ci_nfii=0)
        architecture.vine_petiole(mtg_vine, v)
        architecture.vine_leaf(mtg_vine, v, leaf_inc=leaf_inc, lim_max=lim_max)
        architecture.vine_mtg_properties(mtg_vine, v)
        architecture.vine_mtg_geometry(mtg_vine, v)
        architecture.vine_transform(mtg_vine, v)

    scene_pgl = display.visu(mtg_vine, def_elmnt_color_dict=True, scene=Scene(), view_result=False)

    return mtg_vine, scene_pgl


def create_mockup(path_digit: Path, params_architecture: dict, path_preprocessed_dir: Path):
    path_preprocessed = path_preprocessed_dir / f'combi_{params_architecture["id"]}'
    path_preprocessed.mkdir(parents=True, exist_ok=True)

    grapevine_mtg, pgl_scene = build_mtg(
        path_digit=path_digit,
        a_L=params_architecture['a_L'],
        b_L=params_architecture['b_L'],
        leaf_inc=params_architecture['leaf_inc'],
        lim_max=params_architecture['lim_max'])
    architecture.mtg_save_geometry(scene=pgl_scene, file_path=path_preprocessed)
    architecture.save_mtg(g=grapevine_mtg, scene=pgl_scene, file_path=path_preprocessed, filename=f'initial_mtg.pckl')
    pass


def preprocess_static(path_weather: Path, params_architecture: dict, path_preprocessed_dir: Path,
                      user_params: dict, nitrogen_content: float = None):
    print("Computing 'static' data...")
    path_preprocessed = path_preprocessed_dir / f'combi_{params_architecture["id"]}'

    path_mtg = path_preprocessed / 'initial_mtg.pckl'
    path_geometry = path_preprocessed / 'geometry.bgeom'

    grapevine_mtg, pgl_scene = architecture.load_mtg(path_mtg=str(path_mtg), path_geometry=str(path_geometry))

    if nitrogen_content is not None:
        grapevine_mtg.properties()['Na'] = {vid: nitrogen_content for vid in architecture.get_leaves(grapevine_mtg)}

    inputs = io.HydroShootInputs(
        g=grapevine_mtg,
        path_project=path_preprocessed_dir,
        path_weather=path_weather,
        user_params=user_params,
        scene=pgl_scene,
        psi_soil=-0.01)
    io.verify_inputs(g=grapevine_mtg, inputs=inputs)

    grapevine_mtg = initialisation.init_model(g=grapevine_mtg, inputs=inputs)

    static_data = {'form_factors': {s: grapevine_mtg.property(s) for s in ('ff_sky', 'ff_leaves', 'ff_soil')}}
    static_data.update({'Na': grapevine_mtg.property('Na')})
    with open(path_preprocessed / f'static.json', mode='w') as f_prop:
        dump(static_data, f_prop, indent=2)

    architecture.mtg_save_geometry(scene=pgl_scene, file_path=path_geometry.parent)
    architecture.save_mtg(g=grapevine_mtg, scene=pgl_scene, file_path=path_mtg.parent, filename=path_mtg.name)

    pass


def preprocess_dynamic(path_weather: Path, params_architecture: dict, path_preprocessed_dir: Path,
                       user_params: dict, date_info: tuple):
    print("Computing 'dynamic' data...")
    path_preprocessed = path_preprocessed_dir / f'combi_{params_architecture["id"]}'

    user_params['simulation'].update({'sdate': date_info[1]})
    user_params['simulation'].update({'edate': date_info[1]})

    grapevine_mtg, pgl_scene = architecture.load_mtg(
        path_mtg=str(path_preprocessed / 'initial_mtg.pckl'),
        path_geometry=str(path_preprocessed / 'geometry.bgeom'))

    inputs = io.HydroShootInputs(
        g=grapevine_mtg,
        path_project=path_preprocessed_dir,
        path_weather=path_weather,
        user_params=user_params,
        scene=pgl_scene,
        psi_soil=-0.01)

    grapevine_mtg.properties()['geometry'] = {k: grapevine_mtg.node(k).geometry
                                              for k in architecture.get_leaves(g=grapevine_mtg)}
    dynamic_data = {}
    inputs_hourly = io.HydroShootHourlyInputs(psi_soil=inputs.psi_soil_forced, sun2scene=inputs.sun2scene)
    for date_sim in inputs.params.simulation.date_range:
        inputs_hourly.update(
            g=grapevine_mtg,
            date_sim=date_sim,
            hourly_weather=inputs.weather[inputs.weather.index == date_sim],
            psi_pd=inputs.psi_pd,
            params=inputs.params)

        grapevine_mtg, diffuse_to_total_irradiance_ratio = initialisation.init_hourly(
            g=grapevine_mtg,
            inputs_hourly=inputs_hourly,
            leaf_ppfd=None,
            params=inputs.params)

        dynamic_data.update({grapevine_mtg.date: {
            'diffuse_to_total_irradiance_ratio': diffuse_to_total_irradiance_ratio,
            'Ei': grapevine_mtg.property('Ei'),
            'Eabs': grapevine_mtg.property('Eabs')}})

    with open(path_preprocessed / f'dynamic_{date_info[0]}.json', mode='w') as f_prop:
        dump(dynamic_data, f_prop, indent=2)
    pass


def get_architectural_params(path_params_archi: Path) -> list[dict]:
    return read_csv(path_params_archi, sep=';', decimal='.').to_dict(orient='records')


def run_preprocess_static(args):
    return preprocess_static(*args)


def run_preprocess_dynamic(args):
    return preprocess_dynamic(*args)


def run_mockups(args):
    return create_mockup(*args)


def mp(sim_args: Iterable, func: Callable, nb_cpu: int = 2):
    with Pool(nb_cpu) as p:
        p.map(func, sim_args)


if __name__ == '__main__':
    path_root = Path(__file__).parent
    is_nitrogen_cst = True
    cfg = ConfigSimVSP()

    params_archi = get_architectural_params(cfg.path_params_architecture)

    time_on = datetime.now()
    mp(sim_args=product([cfg.path_digit], params_archi, [cfg.path_preprocessed_inputs]),
       func=run_mockups,
       nb_cpu=12)
    mp(sim_args=product([cfg.path_weather], params_archi, [cfg.path_preprocessed_inputs],
                        [cfg.params], [cfg.constant_nitrogen_content if is_nitrogen_cst else None]),
       func=run_preprocess_static,
       nb_cpu=12)
    mp(sim_args=product([cfg.path_weather], params_archi, [cfg.path_preprocessed_inputs], [cfg.params], [cfg.dates]),
       func=run_preprocess_dynamic,
       nb_cpu=12)
    time_off = datetime.now()

    print(f"--- Total runtime: {(time_off - time_on).seconds} sec ---")

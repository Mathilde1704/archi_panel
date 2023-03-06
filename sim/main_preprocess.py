from datetime import datetime
from itertools import product
from json import dump
from multiprocessing import Pool
from pathlib import Path
from typing import Iterable

from hydroshoot import io
from hydroshoot.architecture import mtg_save_geometry, save_mtg

from archi_panel.simulator import initialisation_twins
from archi_panel.utils import copy_mtg, extract_mtg
from config import Config2021
from example.common import build_mtg


def run_preprocess(params: dict, path_digit: Path, path_project: Path, path_preprocessed_inputs: Path):
    id_mtg = path_digit.stem
    g, scene = build_mtg(path_file=path_digit, is_show_scene=False)
    mtg_save_geometry(scene=scene, file_path=path_preprocessed_inputs, index=f'_{id_mtg}')

    print("Computing 'static' data...")

    inputs = io.HydroShootInputs(
        path_project=path_project,
        user_params=params,
        scene=scene,
        is_write_result=False,
        path_output_file=Path(),
        psi_soil=-.01)
    io.verify_inputs(g=g, inputs=inputs)

    g_clone = copy_mtg(g)
    g = extract_mtg(g, plant_id=1)

    print("Computing 'static' data...")

    g, g_clone = initialisation_twins.init_model(g=g, g_clone=g_clone, inputs=inputs)
    static_data = {'form_factors': {s: g.property(s) for s in ('ff_sky', 'ff_leaves', 'ff_soil')}}
    static_data.update({'Na': g.property('Na')})
    with open(path_preprocessed_inputs / f'{id_mtg}_static.json', mode='w') as f_prop:
        dump(static_data, f_prop, indent=2)

    save_mtg(g=g, scene=scene, file_path=path_preprocessed_inputs, filename=f'initial_mtg_{id_mtg}.pckl')

    print("Computing 'dynamic' data...")
    dynamic_data = {}

    inputs_hourly = io.HydroShootHourlyInputs(psi_soil=inputs.psi_soil_forced, sun2scene=inputs.sun2scene)

    params = inputs.params
    for date in params.simulation.date_range:
        print("=" * 72)
        print(f'Date: {date}\n')

        inputs_hourly.update(g=g, date_sim=date, hourly_weather=inputs.weather[inputs.weather.index == date],
                             psi_pd=inputs.psi_pd, params=params)

        g, diffuse_to_total_irradiance_ratio = initialisation_twins.init_hourly(
            g=g, g_clone=g_clone, inputs_hourly=inputs_hourly, leaf_ppfd=inputs.leaf_ppfd, params=params)

        dynamic_data.update({g.date: {
            'diffuse_to_total_irradiance_ratio': diffuse_to_total_irradiance_ratio,
            'Ei': g.property('Ei'),
            'Eabs': g.property('Eabs')}})

    with open(path_preprocessed_inputs / f'{id_mtg}_dynamic.json', mode='w') as f_prop:
        dump(dynamic_data, f_prop, indent=2)

    pass


def run_sims(args):
    return run_preprocess(*args)


def mp(sim_args: Iterable, nb_cpu: int = 2):
    with Pool(nb_cpu) as p:
        p.map(run_sims, sim_args)


if __name__ == '__main__':
    path_root = Path(__file__).parent.resolve()
    cfg = Config2021()

    time_on = datetime.now()
    mp(sim_args=product([cfg.params], cfg.digit_files, [path_root.resolve()], [cfg.path_preprocessed_inputs]),
       nb_cpu=4)
    time_off = datetime.now()
    print(f"--- Total runtime: {(time_off - time_on).seconds} sec ---")

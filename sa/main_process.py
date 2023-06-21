from datetime import datetime
from itertools import product
from json import load as load_json
from multiprocessing import Pool
from pathlib import Path
from typing import Iterable

from hydroshoot import architecture, model

import config


def run_hydroshoot(path_weather: Path, user_params: dict, path_preprocessed_dir: Path, params_architecture: tuple,
                   path_output_dir: Path, date_info: tuple, is_hydraulic: bool):
    id_sim, *_ = params_architecture

    path_preprocessed = path_preprocessed_dir / f'combi_{id_sim}'

    user_params['simulation'].update({'sdate': f"{date_info[1]} 00:00:00"})
    user_params['simulation'].update({'edate': f"{date_info[1]} 23:00:00"})

    if is_hydraulic:
        user_params["simulation"].update({"hydraulic_structure": True, "negligible_shoot_resistance": False})
        user_params["exchange"]["par_gs"]['model'] = "misson"
        user_params["soil"]["avg_root_radius"] = 0.001
        user_params["soil"]["root_length"] = 3000

    g, scene = architecture.load_mtg(
        path_mtg=str(path_preprocessed / 'initial_mtg.pckl'),
        path_geometry=str(path_preprocessed / 'geometry.bgeom'))

    with open(path_preprocessed / 'static.json', mode='r') as f:
        static_inputs = load_json(f)
    with open(path_preprocessed / f'dynamic_{date_info[0]}.json', mode='r') as f:
        dynamic_inputs = load_json(f)

    path_output = path_output_dir / date_info[0] / f'combi_{id_sim}'
    path_output.mkdir(parents=True, exist_ok=True)

    model.run(
        g=g,
        wd=path_preprocessed_dir.parent,
        path_weather=path_weather,
        params=user_params,
        scene=scene,
        write_result=True,
        path_output=path_output / 'time_series.csv',
        psi_soil_init=-0.01,
        form_factors=static_inputs['form_factors'],
        leaf_nitrogen=static_inputs['Na'],
        leaf_ppfd=dynamic_inputs)

    pass


def run_sims(args):
    return run_hydroshoot(*args)


def mp(sim_args: Iterable, nb_cpu: int = 2):
    with Pool(nb_cpu) as p:
        p.map(run_sims, sim_args)


if __name__ == '__main__':
    is_consider_hydraulic_network: bool = True

    path_root = Path(__file__).parent
    cfg = config.ConfigSensitivityAnalysis(is_on_remote=False)
    params = config.Params()
    params_archi = params.combinations

    path_outputs = cfg.path_outputs.parent / "_".join((cfg.path_outputs.name,
                                                       f"{'psi' if is_consider_hydraulic_network else 'vpd'}"))

    time_on = datetime.now()
    mp(sim_args=product([cfg.path_weather], [cfg.params], [cfg.path_preprocessed_inputs], params_archi,
                        [cfg.path_outputs], cfg.dates, [is_consider_hydraulic_network]),
       nb_cpu=12)
    time_off = datetime.now()
    print(f"--- Total runtime: {(time_off - time_on).seconds} sec ---")

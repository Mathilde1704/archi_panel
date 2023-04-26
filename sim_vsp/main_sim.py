from datetime import datetime
from itertools import product
from json import load
from multiprocessing import Pool
from pathlib import Path
from typing import Iterable

from hydroshoot import architecture, model

from config import ConfigSimVSP
from main_preprocess import get_architectural_params


def run_hydroshoot(path_weather: Path, params: dict, path_preprocessed_dir: Path, id_sim: int, path_output_dir: Path,
                   date_info: tuple):
    path_preprocessed = path_preprocessed_dir / f'combi_{id_sim}'

    params['simulation'].update({'sdate': date_info[1]})
    params['simulation'].update({'edate': date_info[1]})

    g, scene = architecture.load_mtg(
        path_mtg=str(path_preprocessed / 'initial_mtg.pckl'),
        path_geometry=str(path_preprocessed / 'geometry.bgeom'))

    with open(path_preprocessed / 'static.json') as f:
        static_inputs = load(f)
    with open(path_preprocessed / f'dynamic_{date_info[0]}.json') as f:
        dynamic_inputs = load(f)

    path_output = path_output_dir / date_info[0] / f'combi_{id_sim}'
    path_output.mkdir(parents=True, exist_ok=True)

    model.run(
        g=g,
        wd=path_preprocessed_dir.parent,
        path_weather=path_weather,
        params=params,
        scene=scene,
        write_result=True,
        path_output=path_output / 'time_series.csv',
        psi_soil=-0.1,
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
    path_root = Path(__file__).parent
    cfg = ConfigSimVSP()

    ids = sorted([v['id'] for v in get_architectural_params(cfg.path_params_architecture)])

    time_on = datetime.now()
    mp(sim_args=product(
        [cfg.path_weather], [cfg.params], [cfg.path_preprocessed_inputs], ids, [cfg.path_outputs], cfg.dates),
        nb_cpu=12)
    time_off = datetime.now()
    print(f"--- Total runtime: {(time_off - time_on).seconds} sec ---")

from datetime import datetime
from itertools import product
from json import load
from multiprocessing import Pool
from pathlib import Path
from typing import Iterable

from hydroshoot.architecture import load_mtg

from archi_panel.simulator import hydroshoot_wrapper
from config import ConfigSim


def run_hydroshoot(params: dict, path_preprocessed_dir: Path, id_digit: str, path_output_dir: Path,
                   is_constant_nitrogen: bool = False):
    sim_cfg = ConfigSim(year=year)
    g, scene = load_mtg(
        path_mtg=str(path_preprocessed_dir / f'initial_mtg_{id_digit}.pckl'),
        path_geometry=str(path_preprocessed_dir / f'geometry_{id_digit}.bgeom'))

    with open(path_preprocessed_dir / f'{id_digit}_static.json') as f:
        static_inputs = load(f)
    with open(path_preprocessed_dir / f'{id_digit}_dynamic.json') as f:
        dynamic_inputs = load(f)

    if is_constant_nitrogen:
        static_inputs['Na'] = {k: sim_cfg.constant_nitrogen_content for k in static_inputs['Na'].keys()}
        path_output = path_output_dir / 'cst_nitrogen' / id_digit
    else:
        path_output = path_output_dir / id_digit

    path_output.mkdir(parents=True, exist_ok=True)

    hydroshoot_wrapper.run(
        g=g,
        wd=path_preprocessed_dir.parent,
        params=params,
        plant_id=1,
        scene=scene,
        is_write_result=True,
        is_write_mtg=True,
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
    for year in (2021, 2022):
        cfg = ConfigSim(year=year)
        is_cst_n = True

        time_on = datetime.now()
        mp(sim_args=product(
            [cfg.params], [cfg.path_preprocessed_inputs], cfg.digit_ids, [cfg.path_outputs_dir], [is_cst_n]),
           nb_cpu=12)
        time_off = datetime.now()
        print(f"--- Total runtime: {(time_off - time_on).seconds} sec ---")

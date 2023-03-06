from json import load, dump
from pathlib import Path

from hydroshoot import io
from openalea.mtg.mtg import MTG
from openalea.plantgl.all import Scene

from archi_panel.simulator import hydroshoot_wrapper
from archi_panel.simulator import initialisation_twins
from archi_panel.utils import copy_mtg, extract_mtg
from example.common import build_mtg


def run_preprocess(g: MTG, path_project: Path, pgl_scene: Scene,
                   path_preprocessed_inputs: Path, id_mtg: str) -> MTG:
    path_preprocessed_inputs.mkdir(parents=True, exist_ok=True)

    with open(path_project / 'params_default.json', mode='r') as f:
        params = load(f)

    print("Computing 'static' data...")

    inputs = io.HydroShootInputs(
        path_project=path_project,
        user_params=params,
        scene=pgl_scene,
        is_write_result=False,
        path_output_file=Path(),
        psi_soil=-.01)
    io.verify_inputs(g=g, inputs=inputs)

    g_clone = copy_mtg(g)
    g = extract_mtg(g, plant_id=1)

    g, g_clone = initialisation_twins.init_model(g=g, g_clone=g_clone, inputs=inputs)
    static_data = {'form_factors': {s: g.property(s) for s in ('ff_sky', 'ff_leaves', 'ff_soil')}}
    static_data.update({'Na': g.property('Na')})
    with open(path_preprocessed_inputs / f'{id_mtg}_static.json', mode='w') as f_prop:
        dump(static_data, f_prop, indent=2)
    pass

    print("Computing 'dynamic' data...")
    dynamic_data = {}

    inputs_hourly = io.HydroShootHourlyInputs(psi_soil=inputs.psi_soil_forced, sun2scene=inputs.sun2scene)

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

    return g


if __name__ == '__main__':
    path_root = Path(__file__).parent
    path_data = path_root.parent / 'data'

    path_digit = Path(r'C:\Users\albashar\Documents\dvp\archi_panel\data\real_plants\digit\year_2021')

    for path_file in path_digit.iterdir():
        print(path_file.name)
        grapevine_mtg, scene = build_mtg(path_file=path_file, is_show_scene=False)
        run_preprocess(
            g=grapevine_mtg,
            path_project=path_root,
            pgl_scene=scene,
            path_preprocessed_inputs=path_root / 'preprocessed_data',
            id_mtg=path_file.stem)

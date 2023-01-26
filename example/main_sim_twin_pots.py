"""This is an example on running HydroShoot on two adjacent grapevine pots on the same row (twin pots)."""

from pathlib import Path

from openalea.mtg.mtg import MTG

from archi_panel.simulator import hydroshoot_wrapper
from example.common import build_mtg


def handle_twin_pots(g: MTG, plant_id: int) -> MTG:
    pass


if __name__ == '__main__':
    path_project = Path(__file__).parent
    path_preprocessed_data = path_project / 'preprocessed_inputs'
    is_preprocess_data = False

    g, scene = build_mtg(path_file=path_project / 'digit_twin_pots.csv', is_show_scene=False)
    hydroshoot_wrapper.run(
        g=g,
        wd=path_project,
        plant_id=1,
        scene=scene,
        is_write_result=True,
        is_write_mtg=False,
        path_output=path_project / 'output_twins/time_series.csv',
        psi_soil=-0.5,
        gdd_since_budbreak=100)

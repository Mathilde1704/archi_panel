from pathlib import Path

from hydroshoot.architecture import get_leaves, load_mtg
from numpy import mean, arcsin, degrees
from openalea.plantgl.all import surface, Viewer


def calc_surface_foliaire_totale(mtg_vigne):
    total_leaf_area = 0
    for vid in mtg_vigne.VtxList(Scale=3):
        n = mtg_vigne.node(vid)
        if n.label.startswith('L'):
            total_leaf_area += surface(n.geometry)
    return total_leaf_area * 1.e-4


def _calc_inclinaison_foliaire(node):
    position_tip = node.properties()['TopPosition']
    position_bas = node.properties()['BotPosition']

    lobe_length = (sum([(position_tip[i] - position_bas[i]) ** 2 for i in range(3)])) ** 0.5
    height_diff = position_tip[-1] - position_bas[-1]
    return degrees(arcsin(-height_diff / lobe_length))


def calc_inclinaison_foliaire(mtg_vigne):
    return mean([_calc_inclinaison_foliaire(mtg_vigne.node(i)) for i in get_leaves(g=mtg_vigne)])


def calc_longueur_intrenoeuds(mtg_vigne):
    return mean([mtg_vigne.node(i).properties()['Length'] for i in get_leaves(g=mtg_vigne, leaf_lbl_prefix='inI')])


if __name__ == '__main__':
    path_root = Path(__file__).parent

    combi_id = 27

    g, scene = load_mtg(
        path_mtg=str(path_root / 'preprocessed_data' / f'combi_{combi_id}/initial_mtg.pckl'),
        path_geometry=str(path_root / f'preprocessed_data/combi_{combi_id}/geometry.bgeom'))

    sf = calc_surface_foliaire_totale(g)  # m2
    len = calc_longueur_intrenoeuds(g)  # cm
    r = calc_inclinaison_foliaire(g)  # °

    print(f'SF: {sf:.3f}', f'LEN: {len:.3f}', f'R: {r:.3f}')
    Viewer.display(scene)
    pass

from pathlib import Path

from hydroshoot import architecture, display
from hydroshoot.architecture import get_leaves
from numpy import mean, arcsin, degrees
from openalea.mtg import traversal
from openalea.plantgl.all import Scene, surface


def calc_surface_foliaire(mtg_vigne):
    leaf_area = [surface(mtg_vigne.node(vid).geometry) for vid in get_leaves(mtg_vigne)]
    return sum(leaf_area), mean(leaf_area)


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


def build_mtg(path_digit, N_max, in_order_max, slope_nfii, a_L, b_L, leaf_inc):
    g = architecture.vine_mtg(path_digit)

    for v in traversal.iter_mtg2(g, g.root):
        architecture.vine_phyto_modular(g, v)
        architecture.vine_axeII(g, v, N_max=N_max, in_order_max=in_order_max, slope_nfii=slope_nfii, a_L=a_L, b_L=b_L)
        architecture.vine_petiole(g, v)
        architecture.vine_leaf(g, v, leaf_inc=leaf_inc)
        architecture.vine_mtg_properties(g, v)
        architecture.vine_mtg_geometry(g, v)
        architecture.vine_transform(g, v)

    scene = display.visu(g, def_elmnt_color_dict=True, scene=Scene(), view_result=True)

    return g, scene


if __name__ == '__main__':
    path_root = Path(__file__).parent
    g, scene = build_mtg(
        path_digit=r'C:\Users\albashar\Documents\dvp\hydroshoot\example\vsp_ww_grapevine\digit.input',
        N_max=3,
        in_order_max=5,
        slope_nfii=2.8,
        a_L=43.718,
        b_L=-37.663,
        leaf_inc=-30.0)

    sf_tot, sf_avg = calc_surface_foliaire(g)  # m2
    len = calc_longueur_intrenoeuds(g)  # cm
    r = calc_inclinaison_foliaire(g)  # °

    print(f'SF_tot: {sf_tot:.1f}', f'SF_avg: {sf_avg:.1f}', f'LEN: {len:.3f}', f'R: {r:.3f}')

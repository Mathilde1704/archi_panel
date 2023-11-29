from pathlib import Path

from hydroshoot import architecture, display
from numpy import array
from openalea.mtg import traversal, mtg
from openalea.plantgl.all import Scene


def build_reference_mtg(path_digit: Path) -> tuple[mtg.MTG, Scene]:
    mtg_vine = architecture.vine_mtg(path_digit)

    for v in traversal.iter_mtg2(mtg_vine, mtg_vine.root):
        architecture.vine_phyto_modular(mtg_vine, v)
        architecture.vine_axeII(mtg_vine, v, ci_nfii=0)
        architecture.vine_petiole(mtg_vine, v)
        architecture.vine_leaf(mtg_vine, v)
        architecture.vine_mtg_properties(mtg_vine, v)
        architecture.vine_mtg_geometry(mtg_vine, v)
        architecture.vine_transform(mtg_vine, v)

    scene_pgl = display.visu(mtg_vine, def_elmnt_color_dict=True, scene=Scene(), view_result=False)

    return mtg_vine, scene_pgl


def get_shoot_node_ids(g: mtg.MTG) -> list:
    return [v for v in g.VtxList(Scale=2) if g.node(v).label.startswith('sh')]


def get_annual_shoot_internode_lengths(g: mtg.MTG) -> list:
    return [g.node(v2._vid).Length for v1 in get_shoot_node_ids(g) for v2 in g.node(v1).components() if
            g.node(v2._vid).label.startswith('in')]


def calc_reference_mtg_internode_length(path_digit: Path) -> float:
    reference_mtg, _ = build_reference_mtg(path_digit=path_digit)
    annual_shoot_internode_lengths = get_annual_shoot_internode_lengths(g=reference_mtg)
    return sum(annual_shoot_internode_lengths) / len(annual_shoot_internode_lengths)


def build_mtg2(path_digit: Path, leaf_inc: float, lim_max: float, scale: float = 1) -> tuple:
    mtg_vine = architecture.vine_mtg(path_digit)
    cordon = architecture.cordon_vector(g=mtg_vine)[-1]

    for v in traversal.iter_mtg2(mtg_vine, mtg_vine.root):
        # architecture.vine_phyto_modular(mtg_vine, v)
        architecture.vine_axeII(mtg_vine, v, ci_nfii=0)
        architecture.vine_petiole(mtg_vine, v)
        architecture.vine_leaf(mtg_vine, v, leaf_inc=leaf_inc, lim_max=lim_max, cordon_vector=cordon)

    mtg_vine = scale_mtg(g=mtg_vine, scale=scale)

    for v in traversal.iter_mtg2(mtg_vine, mtg_vine.root):
        architecture.vine_mtg_properties(mtg_vine, v)
        architecture.vine_mtg_geometry(mtg_vine, v)
        architecture.vine_transform(mtg_vine, v)

    scene_pgl = display.visu(mtg_vine, def_elmnt_color_dict=True, scene=Scene(), view_result=False)

    return mtg_vine, scene_pgl


def calc_vectors(g: mtg.MTG, vid_start: int) -> dict:
    res = {}
    for vid in list(traversal.iter_mtg2(mtg=g, vtx_id=vid_start))[1:]:
        n = g.node(vid)
        p = n.parent()
        res.update({vid: array(n.TopPosition) - array(p.TopPosition)})

    return res


def scale_mtg(g: mtg.MTG, scale: float) -> mtg.MTG:
    """Scales mtg's TopPosition's.

    Args:
        g: mtg object
        scale: scale to be applied (greater than 0)

    Returns:
        scaled mtg

    Notes:
        This function MUST be applied BEFORE that of 'vine_mtg_properties()'

    """
    vectors = {vid_start: calc_vectors(g=g, vid_start=vid_start) for vid_start in get_shoot_node_ids(g=g)}
    for vid_start in get_shoot_node_ids(g=g):
        for vid in list(traversal.iter_mtg2(mtg=g, vtx_id=vid_start))[1:]:
            n = g.node(vid)
            p = n.parent()
            n.TopPosition = list(p.TopPosition + vectors[vid_start][vid] * (
                scale if not n.label.startswith(('L', 'Pet')) else 1))

    return g

from openalea.mtg.mtg import MTG


def trim_mtg(g: MTG, vtx_id: int):
    """This function trims branches at ALL scales greater than zero."""
    if g.node(vtx_id).scale() != 0:
        if g.node(vtx_id).nb_components() == 0:
            complex_id = g.node(vtx_id).complex()._vid
            g.node(vtx_id).remove_tree()
            trim_mtg(g, complex_id)
        else:
            trim_mtg(g, g.node(vtx_id).components()[0]._vid)
    pass


def copy_mtg(g: MTG) -> MTG:
    geom = {vid: g.node(vid).geometry for vid in g.property('geometry')}
    g.remove_property('geometry')
    g_copy = g.copy()
    g.add_property('geometry')
    g.property('geometry').update(geom)
    g_copy.add_property('geometry')
    g_copy.property('geometry').update(geom)
    return g_copy


def extract_mtg(g: MTG, plant_id: int) -> MTG:
    g_single = copy_mtg(g=g)

    branch_vid_to_remove = [vid for vid in g.VtxList(Scale=1) if g.node(vid).label != f'plant{plant_id}']
    for vid in branch_vid_to_remove:
        trim_mtg(g=g_single, vtx_id=vid)

    return g_single


def print_progress_bar(iteration: int, total: int, prefix: str = '', suffix: str = '', decimals: int = 1,
                       length: int = 100, fill: str = '█', print_end: str = "\r"):
    """Call in a loop to create terminal progress bar

    Args:
        iteration: current iteration
        total: total iterations
        prefix: prefix string
        suffix: suffix string
        decimals: positive number of decimals in percent complete
        length: character length of bar
        fill: bar fill character
        print_end: end character (e.g. "\r", "\r\n")

    References:
        https://stackoverflow.com/questions/3173320/text-progress-bar-in-terminal-with-block-characters
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=print_end)
    # Print New Line on Complete
    if iteration == total:
        print('')

    pass

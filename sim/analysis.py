from json import load
from pathlib import Path

from hydroshoot.architecture import load_mtg, get_leaves
from numpy import mean, std, arcsin, arccos, degrees
from openalea.mtg.mtg import _ProxyNode
from openalea.plantgl.all import surface
from pandas import read_csv, concat, to_datetime, DataFrame

from sim.config import ConfigSim


def calc_leaf_inclination(node: _ProxyNode) -> float:
    position_tip = node.properties()['TopPosition']
    position_bas = node.properties()['BotPosition']

    lobe_length = (sum([(position_tip[i] - position_bas[i]) ** 2 for i in range(3)])) ** 0.5
    height_diff = position_tip[-1] - position_bas[-1]
    return degrees(arcsin(-height_diff / lobe_length))


def calc_leaf_azimuth(node: _ProxyNode) -> float:
    # Angle convention
    #
    #          ------------------->  East
    #          |
    #          o  lobe base
    #         /|\
    #        / | \
    #       /  |  \
    #      /   |   \
    #     /    |    \
    #    o (+) | (-) o  lobe tip
    #          |
    #         \|/
    #          V
    #        South

    position_tip = node.properties()['TopPosition']
    position_bas = node.properties()['BotPosition']
    lobe_horizontal_length = (sum([(position_tip[i] - position_bas[i]) ** 2 for i in range(2)])) ** 0.5
    delta_x = position_tip[0] - position_bas[0]
    delta_y = position_tip[1] - position_bas[1]
    angle_from_south = arccos(delta_x / lobe_horizontal_length)

    return degrees(angle_from_south if delta_y <= 0 else - angle_from_south)


def concatenate_time_series(pth_outputs: Path):
    df_weather = read_csv(pth_outputs.parents[2] / 'data/weather.csv',
                          sep=';', decimal='.', parse_dates=['time'], index_col='time')

    dfs = []
    for year in (2021, 2022):
        for pth in (pth_outputs / f'{year:.0f}').iterdir():
            df = read_csv(pth / 'time_series.csv', sep=';', decimal='.')
            df.loc[:, 'id_digit'] = pth.stem
            df.rename(columns={'Unnamed: 0': 'time'}, inplace=True)
            df.loc[:, 'time'] = to_datetime(df['time'])

            df.loc[:, 'Tair'] = df_weather.loc[df['time'], 'Tac'].values
            dfs.append(df)

    df_total = concat(dfs)
    df_total['dTc_air'] = df_total['Tleaf'] - df_total['Tair']
    df_total.to_csv(pth_outputs / 'time_series_all.csv', sep=';', decimal='.', index=False)
    pass


def get_mockups_summary(pth_root: Path, is_cst_nitrogen: bool):
    dfs = []
    for year in (2021, 2022):
        cfg = ConfigSim(year=year)
        path_preprocessed_dir = cfg.path_preprocessed_inputs
        for i, id_digit in enumerate(cfg.digit_ids):
            with open(path_preprocessed_dir / f'{id_digit}_static.json') as f:
                static_data = load(f)
            if is_cst_nitrogen:
                nitrogen_content = [cfg.constant_nitrogen_content] * len(static_data['Na'].values())
            else:
                nitrogen_content = list(static_data['Na'].values())

            g, scene = load_mtg(
                path_mtg=str(path_preprocessed_dir / f'initial_mtg_{id_digit}.pckl'),
                path_geometry=str(path_preprocessed_dir / f'geometry_{id_digit}.bgeom'))

            inclination_ls = []
            leaf_area_ls = []
            azimuth_ls = []
            for id_leaf in get_leaves(g):
                node_leaf = g.node(id_leaf)
                inclination_ls.append(calc_leaf_inclination(node_leaf))
                leaf_area_ls.append(surface(node_leaf.geometry) * 1.e-4)
                azimuth_ls.append(calc_leaf_azimuth(node_leaf))

            internode_lengths = [g.node(i).properties()['Length'] for i in get_leaves(g=g, leaf_lbl_prefix='inI')]

            dfs.append(DataFrame(dict(
                id_digit=id_digit,
                leaf_inclination_mean=mean(inclination_ls),
                leaf_inclination_std=std(inclination_ls),
                internode_length_mean=mean(internode_lengths),
                internode_length_std=std(internode_lengths),
                leaf_area_mean=mean(leaf_area_ls),
                leaf_area_std=std(leaf_area_ls),
                leaf_nitrogen_mean=mean(nitrogen_content),
                leaf_nitrogen_std=std(nitrogen_content),
                leaf_azimuth_mean=mean(azimuth_ls),
                leaf_azimuth_std=std(azimuth_ls)),
                index=[i]))

    df_total = concat(dfs)
    df_total.to_csv(pth_root / f"outputs/{'nitrogen_constant' if is_cst_nitrogen else 'nitrogen_variable'}/summary.csv",
                    sep=';', decimal='.', index=False)
    pass


if __name__ == '__main__':
    path_root = Path(__file__).parent
    is_constant_nitrogen = True

    path_outputs = path_root / 'outputs' / ('nitrogen_constant' if is_constant_nitrogen else 'nitrogen_variable')

    concatenate_time_series(pth_outputs=path_outputs)
    get_mockups_summary(pth_root=path_root, is_cst_nitrogen=is_constant_nitrogen)

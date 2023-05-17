from pathlib import Path
from pickle import load

from hydroshoot.architecture import get_leaves
from numpy import quantile
from pandas import concat, DataFrame, read_csv

from config import ConfigSimVSP


def get_all_time_series(path_outputs: Path):
    combis = [pth for pth in path_outputs.iterdir() if pth.stem.startswith('combi_')]
    res = None
    for pth in combis:
        pth_file = pth / 'time_series.csv'
        df = read_csv(pth_file, sep=';', decimal='.', parse_dates=[0])
        df.loc[:, 'combi'] = pth.name.split('_')[-1]
        if res is None:
            res = df
        else:
            res = concat([res, df])
    res.rename(columns={'Unnamed: 0': 'time'}, inplace=True)
    res.to_csv(path_outputs / 'time_series_all.csv', index=False, sep=';', decimal='.')
    pass


def get_temperature_summary(path_data: Path, mtg_index: str) -> None:
    res = {s: [] for s in ('dt', 'combi', 't_q0', 't_q10', 't_q50', 't_q90', 't_q100')}
    combis = [pth for pth in path_data.iterdir() if (pth.is_dir() and pth.stem.startswith('combi_'))]
    for pth in combis:
        with open(pth / f'mtg{mtg_index}.pckl', mode='rb') as f:
            g, _ = load(f)
        print(pth)
        t_leaves = list(g.property("Tlc").values())
        res['dt'].append(g.date)
        res['combi'].append(pth.name)
        res['t_q0'].append(quantile(t_leaves, 0))
        res['t_q10'].append(quantile(t_leaves, 0.1))
        res['t_q50'].append(quantile(t_leaves, 0.5))
        res['t_q90'].append(quantile(t_leaves, 0.9))
        res['t_q100'].append(quantile(t_leaves, 1.))
    DataFrame(res).to_csv(path_data / 'summary_temperature.csv', sep=';', decimal='.', index=False)

    pass


def get_temperature_summary2(path_data: Path, mtg_index: str) -> None:
    combis = [pth for pth in path_data.iterdir() if (pth.is_dir() and pth.stem.startswith('combi_'))]
    with open(path_data / f'combi_1/mtg{mtg_index}.pckl', mode='rb') as f:
        g, _ = load(f)
    ids = get_leaves(g)
    res = {'leaf_id': ids}

    for pth in combis:
        with open(pth / f'mtg{mtg_index}.pckl', mode='rb') as f:
            g, _ = load(f)
        print(pth)
        res[pth.name] = [g.node(i).Tlc for i in ids]
    DataFrame(res).to_csv(path_data / 'summary_temperature2.csv', sep=';', decimal='.', index=False)

    pass


def get_all_leaf_props(path_data: Path, mtg_index: str) -> None:
    combis = [pth for pth in path_data.iterdir() if (pth.is_dir() and pth.stem.startswith('combi_'))]
    for pth in combis:
        with open(pth / f'mtg{mtg_index}.pckl', mode='rb') as f:
            g, _ = load(f)
        ids = get_leaves(g)
        res = {'leaf_id': ids}
        print(pth)

        for s in ('TopPosition', 'BotPosition', 'Length', 'Na', 'ff_sky', 'ff_leaves', 'ff_soil', 'Flux', 'Vcm25',
                  'Jm25', 'TPU25', 'Rd', 'u', 'Eabs', 'psi_head', 'gbH', 'Tlc', 'An', 'gs', 'gb', 'E', 'leaf_area'):
            res.update({s: [g.node(i).properties()[s] for i in ids]})
            DataFrame(res).to_csv(path_data / f'summary_props_{pth.name}.csv', sep=';', decimal='.', index=False)

    pass


if __name__ == '__main__':
    cfg = ConfigSimVSP()
    for sky_condition, date_sim in cfg.dates:
        path_outputs_dir = cfg.path_outputs / sky_condition
        index_mtg = date_sim.replace('-', '').replace(':', '').replace(' ', '')
        get_all_time_series(path_outputs=path_outputs_dir)
        get_temperature_summary(path_data=path_outputs_dir, mtg_index=index_mtg)
        get_temperature_summary2(path_data=path_outputs_dir, mtg_index=index_mtg)
        get_all_leaf_props(path_data=path_outputs_dir, mtg_index=index_mtg)

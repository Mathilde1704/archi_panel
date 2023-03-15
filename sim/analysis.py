from pathlib import Path

from pandas import read_csv, concat, to_datetime

from sim.config import ConfigSim


def concatenate_time_series(pth_root: Path):
    df_weather = read_csv(pth_root.parent / 'data/weather.csv',
                          sep=';', decimal='.', parse_dates=['time'], index_col='time')

    dfs = []
    for year in (2021, 2022):
        cfg = ConfigSim(year=year)

        for pth in cfg.path_outputs_dir.iterdir():
            df = read_csv(pth / 'time_series.csv', sep=';', decimal='.')
            df.loc[:, 'id_digit'] = pth.stem
            df.rename(columns={'Unnamed: 0': 'time'}, inplace=True)
            df.loc[:, 'time'] = to_datetime(df['time'])

            df.loc[:, 'Tair'] = df_weather.loc[df['time'], 'Tac'].values
            dfs.append(df)

    df_total = concat(dfs)
    df_total['dTc_air'] = df_total['Tleaf'] - df_total['Tair']
    df_total.to_csv(pth_root / 'outputs/time_series_all.csv', sep=';', decimal='.', index=False)
    pass


if __name__ == '__main__':
    path_root = Path(__file__).parent
    concatenate_time_series(pth_root=path_root)

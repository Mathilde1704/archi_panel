from pandas import read_csv
from pathlib import Path
from datetime import datetime


def create_weather_scenarios() -> None:
    path_root = Path(__file__).parent
    weather_2019 = read_csv(path_root / 'weather_2019.csv',
                            sep=';', decimal='.', parse_dates=['time'], index_col='time')

    scenarios = [
        ('hot', 'mean_data_hot_35.csv'),
        ('very_hot', 'mean_data_hot_37.csv'),
        ('extremely_hot', 'mean_data_hot_45.csv')]

    for scenario, file_name in scenarios:
        df = read_csv(path_root / f'source/{file_name}', sep=';', decimal='.')
        df.loc[:, 'datetime'] = df['heure'].apply(lambda x: datetime.strptime(f'2019-06-28 {x}', '%Y-%m-%d %H:%M:%S'))
        df.set_index('datetime', inplace=True)
        df.loc[:, 'Rg_2'] = df['Rg_2'].apply(lambda x: max(0, x))

        df2 = weather_2019.copy(deep=True)
        df2.loc[df.index, 'Tac'] = df.loc[:, 'Tmoy'].to_list()
        df2.loc[df.index, 'u'] = df.loc[:, 'Vent'].to_list()
        df2.loc[df.index, 'Rg'] = df.loc[:, 'Rg_2'].to_list()
        df2.loc[df.index, 'hs'] = df.loc[:, 'RH'].to_list()
        df2.reset_index().to_csv(path_root / f"weather_{scenario}.csv", sep=';', decimal='.', index=False)

    with open(path_root / 'README.txt', mode='w') as f:
        f.write(
            f"# The weather files were automatically generated using:\n"
            f"# ~/{'/'.join([s for s in Path(__file__).parts[-4:]])}.\n"
            "# For each file, data of 2019-06-28 from weather_2019.csv were replaced by those under source/\n"
            f"# {' and '.join(list(zip(*scenarios))[1])}.\n")

    pass


if __name__ == '__main__':
    create_weather_scenarios()

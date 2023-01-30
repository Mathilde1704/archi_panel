from pathlib import Path

from pandas import read_csv

MAP_NAMES = {
    'jour heure (GMT)': 'time',
    'Tmoy (°C)': 'Tac',
    'RH (%)': 'hs',
    'Vent (m/s)': 'u',
    'Précipitations (mm)': 'rainfall',
    'Rg (J/cm²)': 'Rg'}


def preprocess_meteo(path_raw: Path) -> None:
    df = read_csv(path_raw / 'meteo_raw.csv', sep=',', skiprows=5)
    df.rename(columns=MAP_NAMES, inplace=True)
    df.drop('rainfall', axis=1, inplace=True)
    df.loc[:, 'Rg'] = df.apply(lambda x: max(0, x['Rg'] * 10 / 3.6), axis=1)  # J/cm2 -> Wh/m2
    df.to_csv(path_raw.parent / 'meteo.csv', sep=';', decimal='.', index=False)

    pass


if __name__ == '__main__':
    path_root = Path(__file__).parent
    preprocess_meteo(path_raw=path_root)

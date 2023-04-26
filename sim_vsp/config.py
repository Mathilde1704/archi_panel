from json import load
from pathlib import Path


class ConfigSimVSP:
    def __init__(self):
        path_root = Path(__file__).parent.resolve()
        self.path_digit = path_root / 'digit.csv'
        self.path_params_architecture = path_root / 'combinaison_analyses_sensitivite.csv'

        self.path_preprocessed_inputs = path_root / 'preprocessed_data'
        self.path_preprocessed_inputs.mkdir(parents=True, exist_ok=True)

        with open(path_root / 'params.json', mode='r') as f:
            self.params = load(f)

        self.path_outputs = self.path_preprocessed_inputs.parent / f'outputs'
        self.constant_nitrogen_content = 2.2
        self.path_weather = path_root.parent / 'data/weather.csv'
        self.dates = [('clear_sky', "2022-07-11 13:00:00"),
                      ('cloudy_sky', "2021-07-12 13:00:00")]

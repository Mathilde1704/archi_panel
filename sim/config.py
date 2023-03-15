from json import load
from pathlib import Path


class ConfigSim:
    def __init__(self, year: int):
        path_root = Path(__file__).parent.resolve()
        self.path_digit_files = path_root.parent.resolve() / f'data/real_plants/digit/year_{year:.0f}'

        self.path_preprocessed_inputs = path_root / f'preprocessed_data/{year:.0f}'
        self.path_preprocessed_inputs.mkdir(parents=True, exist_ok=True)

        self.path_params = path_root / 'params_default.json'

        self.digit_files = list(self.path_digit_files.iterdir())
        self.digit_ids = [s.stem for s in self.digit_files]

        self.path_outputs_dir = path_root / f'outputs/{year:.0f}'

        with open(self.path_params, mode='r') as f:
            params = load(f)
        params['simulation']['sdate'] = params['simulation']['sdate'].replace('2021-', f'{year}-')
        params['simulation']['edate'] = params['simulation']['edate'].replace('2021-', f'{year}-')
        params['phenology']['emdate'] = params['phenology']['emdate'].replace('2021-', f'{year}-')
        self.params = params

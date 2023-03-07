from json import load
from pathlib import Path


class Config2021:
    def __init__(self):
        path_root = Path(__file__).parent.resolve()
        self.path_digit_files = path_root.parent.resolve() / 'data/real_plants/digit/year_2021'

        self.path_preprocessed_inputs = path_root / 'preprocessed_data'
        self.path_preprocessed_inputs.mkdir(parents=True, exist_ok=True)

        self.path_params = path_root / 'params_default.json'

        self.digit_files = list(self.path_digit_files.iterdir())
        self.digit_ids = [s.stem for s in self.digit_files]

        self.path_outputs_dir = path_root / 'outputs'

        with open(self.path_params, mode='r') as f:
            self.params = load(f)

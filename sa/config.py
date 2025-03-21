from collections import namedtuple
from itertools import product
from json import load
from pathlib import Path

from numpy import linspace
from pandas import read_csv

from funcs import calc_reference_mtg_internode_length


class ConfigSensitivityAnalysis:
    def __init__(self, is_on_remote: bool):
        path_root = Path(__file__).parent.resolve()
        path_relative = '../../../../mnt/data/hydroshoot/project_mathilde_fspm/sa/' if is_on_remote else ''
        self.path_weather_dir = path_root / 'weather_scenarios'

        self.path_preprocessed_inputs = path_root / ''.join((path_relative, 'preprocessed_inputs'))
        self.path_preprocessed_inputs.mkdir(parents=True, exist_ok=True)

        self.path_weather = self.path_weather_dir / 'weather_2019.csv'
        self.constant_nitrogen_content = 2.2
        with open(path_root / 'params.json', mode='r') as f:
            self.params = load(f)
        self.dates = [('clear_sky', "2022-07-11"),
                      ('cloudy_sky', "2021-07-12")]
        self.path_outputs = self.path_preprocessed_inputs.parent / f'outputs'
        self.scenarios_weather = None
        self.scenarios_soil_water_deficit = None
        self.set_scenarios()

    def set_scenarios(self):
        self.scenarios_weather = [(s1, self.path_weather_dir / s2)
                                  for s1, s2 in [('extremely_hot', 'weather_extremely_hot.csv'),
                                                 ('very_hot', 'weather_very_hot.csv'),
                                                 ('hot', 'weather_hot.csv')]]

        self.scenarios_soil_water_deficit = [('mild_wd', -0.3),
                                             ('strong_wd', -0.6)]
        pass


class Params:
    def __init__(self, is_include_real_panel_data: bool = False):
        self.path_root = Path(__file__).parent.resolve()
        self.path_reference_digit = self.path_root / 'digit.csv'

        self._param_values = namedtuple("ParamValues", ['min', 'max', 'bins'])
        self._reference_internode_length = calc_reference_mtg_internode_length(path_digit=self.path_reference_digit)

        self.internode_length = self.get_param_values(min_value=3, max_value=13.5, nb_values=10)
        self.internode_scale = self.get_param_values(
            min_value=self.internode_length.min / self._reference_internode_length,
            max_value=self.internode_length.max / self._reference_internode_length,
            nb_values=10)
        self.limb_inclination = self.get_param_values(min_value=-90, max_value=0, nb_values=10)
        self.leaf_area = self.get_param_values(min_value=50, max_value=350, nb_values=10)
        self.midrib_length = self._param_values(
            min=self.calc_midrib_length(leaf_area=self.leaf_area.min),
            max=self.calc_midrib_length(leaf_area=self.leaf_area.max),
            bins=[self.calc_midrib_length(leaf_area=v) for v in self.leaf_area.bins])

        self._combinations = list(product(self.internode_scale.bins,
                                          self.limb_inclination.bins,
                                          self.midrib_length.bins))
        self.combinations = list(zip(range(len(self._combinations)), *zip(*self._combinations)))

        if is_include_real_panel_data:
            self.add_real_panel_data()

    def get_param_values(self, min_value: float, max_value: float, nb_values: int):
        return self._param_values(min=min_value, max=max_value, bins=linspace(min_value, max_value, nb_values))

    @staticmethod
    def calc_midrib_length(leaf_area: float) -> float:
        """Calculates the midrib length based on limb area.

        Args:
            leaf_area: (cm2) area of the limb

        Returns:
            (cm): midrib length

        """
        return (leaf_area / 0.0107) ** 0.25

    @staticmethod
    def calc_leaf_area(midrib_length: float):
        return 0.0107 * midrib_length ** 4

    def add_real_panel_data(self):
        df = read_csv(self.path_root / 'mathilde_panel.csv', sep=';', decimal='.')

        internode_scale = df['LEN'] / self._reference_internode_length
        limb_inclination = - df['R']
        midrib_length = df['SF'].apply(lambda x: self.calc_midrib_length(leaf_area=x))
        self.combinations += list(zip(df['Genotype'], internode_scale, limb_inclination, midrib_length))
        pass

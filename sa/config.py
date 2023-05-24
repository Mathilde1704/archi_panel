from collections import namedtuple
from itertools import product
from pathlib import Path

from numpy import linspace

from funcs import calc_reference_mtg_internode_length


class ConfigSensitivityAnalysis:
    def __init__(self, is_on_remote: bool):
        path_root = Path(__file__).parent.resolve()
        path_relative = '../../../../mnt/data/hydroshoot/project_mathilde_fspm/sa' if is_on_remote else ''

        self.path_preprocessed_inputs = path_root / '/'.join((path_relative, 'preprocessed_inputs'))
        self.path_preprocessed_inputs.mkdir(parents=True, exist_ok=True)


class Params:
    def __init__(self):
        self.path_reference_digit = Path(__file__).parent.resolve() / 'digit.csv'
        self._param_values = namedtuple("ParamValues", ['min', 'max', 'bins'])
        self._reference_internode_length = calc_reference_mtg_internode_length(path_digit=self.path_reference_digit)

        self.internode_length = self.get_param_values(min_value=3, max_value=13.5, nb_values=10)
        self.internode_scale = self.get_param_values(
            min_value=self.internode_length.min / self._reference_internode_length,
            max_value=self.internode_length.max / self._reference_internode_length,
            nb_values=10)
        self.limb_inclination = self.get_param_values(min_value=0, max_value=90, nb_values=10)
        self.leaf_area = self.get_param_values(min_value=50, max_value=350, nb_values=10)
        self.midrib_length = self._param_values(
            min=self.calc_midrib_length(leaf_area=self.leaf_area.min),
            max=self.calc_midrib_length(leaf_area=self.leaf_area.max),
            bins=[self.calc_midrib_length(leaf_area=v) for v in self.leaf_area.bins])

        self._combinations = list(product(self.internode_scale.bins,
                                          self.limb_inclination.bins,
                                          self.midrib_length.bins))
        self.combinations = list(zip(range(len(self._combinations)), *zip(*self._combinations)))

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

from pathlib import Path
from matplotlib import pyplot as plt

from hydroshoot.exchange import an_gs_ci

PARAMS_PHOTOSYNTHESIS = {"Vcm25": 71.714,
                         "Jm25": 154.894,
                         "TPU25": 11.808,
                         "Rd": 0.914,
                         "alpha": 0.24,
                         "Kc25": 404.9,
                         "Ko25": 278.4,
                         "Tx25": 42.75,
                         "ds": 0.635,
                         "dHd": 200.0,
                         "RespT_Kc": {
                             "c": 38.05,
                             "deltaHa": 79.43
                         },
                         "RespT_Ko": {
                             "c": 20.30,
                             "deltaHa": 36.38
                         },
                         "RespT_Vcm": {
                             "c": 26.35,
                             "deltaHa": 65.33
                         },
                         "RespT_Jm": {
                             "c": 17.57,
                             "deltaHa": 43.54
                         },
                         "RespT_TPU": {
                             "c": 21.46,
                             "deltaHa": 53.1
                         },
                         "RespT_Rd": {
                             "c": 18.72,
                             "deltaHa": 46.39
                         },
                         "RespT_Tx": {
                             "c": 19.02,
                             "deltaHa": 37.83
                         },
                         "photo_inhibition": {
                             "dhd_inhib_beg": 195,
                             "dHd_inhib_max": 190,
                             "psi_inhib_beg": -1.5,
                             "psi_inhib_max": -3,
                             "temp_inhib_beg": 35,
                             "temp_inhib_max": 40
                         }
                         }

PARAMS_STOMAT = {"model": "misson",
                 "g0": 0.02,
                 "m0": 5.278,
                 "psi0": -1.0,
                 "D0": 30.0,
                 "n": 4.0
                 }


def calc_an_gs_ci(ppfd: float, alpha: float = None) -> tuple:
    if alpha is not None:
        PARAMS_PHOTOSYNTHESIS.update({"alpha": alpha})
    return an_gs_ci(air_temperature=25.,
                    absorbed_ppfd=ppfd,
                    relative_humidity=50,
                    leaf_temperature=25.,
                    leaf_water_potential=0.,
                    photo_params=PARAMS_PHOTOSYNTHESIS,
                    gs_params=PARAMS_STOMAT,
                    rbt=2. / 3.,
                    ca=400.)


if __name__ == '__main__':
    path_root = Path(__file__).parent

    ppfd_range = range(0, 2000, 10)
    fig, (ax_an, ax_gs) = plt.subplots(nrows=2, sharex='col')
    for alpha in range(1, 7):
        a = alpha / 10.
        an, *_, gs = zip(*[calc_an_gs_ci(ppfd=v, alpha=a) for v in ppfd_range])
        ax_an.plot(ppfd_range, an, label=a)
        ax_gs.plot(ppfd_range, gs)

    ax_an.set(ylabel='An (umol/m2/s)')
    ax_gs.set(ylabel='gs (umol/m2/s)', xlabel='PPFD (umol/m2/s)')
    ax_an.legend()

    fig.tight_layout()
    fig.savefig(path_root / 'j.png')

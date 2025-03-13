from pathlib import Path
from matplotlib import pyplot as plt
from pandas import read_csv

if __name__ == '__main__':
    path_root = Path(__file__).parent
    fig, axs = plt.subplots(ncols=2, sharex='all')
    for ax, s in zip(axs, ('rand', 'bi')):
        df = read_csv(path_root / f'azimuth_{s}.csv', sep=',')
        ax.hist(df['azimuth'])
        ax.set_title(s)
    axs[0].set(xlabel='azimuth (°)\n(0 at North, positive clockwise)',
               ylabel='freq')
    axs[0].xaxis.set_label_coords(1.3, -0.1, transform=axs[0].transAxes)
    fig.tight_layout()
    fig.savefig(path_root / 'azimuth.png')
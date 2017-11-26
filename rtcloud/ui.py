from nilearn import plotting
import numpy as np
import pandas as pd
import time
from IPython import display


def display_input(nifti, i, fig, ax, cut_coords=None):
    if cut_coords is None:
        cut_coords = [-9]
    plotting.plot_img(nifti, title=i, axes=ax, display_mode="z",
                      cut_coords=cut_coords)
    display.clear_output(wait=True)
    display.display(fig)

def display_output(nifti, i, fig, ax, cut_coords=None):
    if cut_coords is None:
        cut_coords = [-9]
    i = pd.date_range('2013-1-1',periods=100,freq='s')
    ax.clear()
    ax.plot(pd.Series(data=np.random.randn(100), index=i))
    plotting.plot_img(nifti, title=i, axes=ax, display_mode="z",
                      cut_coords=cut_coords)

from ThesisAnalysis import ThesisHDF5Writer, ThesisHDF5Reader, get_plot
from ThesisAnalysis.plotting.setup import ThesisPlotter
import numpy as np
import pandas as pd
import os
from numpy.polynomial.polynomial import polyfit
from matplotlib.colors import LogNorm
from matplotlib.ticker import FuncFormatter
from IPython import embed


class ScatterPlotter(ThesisPlotter):
    def plot(self, x, y):
        self.ax.scatter(x, y, s=0.5)


def process(paths, nsb):
    ff_m = []
    ff_c = []
    for p in paths:
        with ThesisHDF5Reader(p) as reader:
            df = reader.read("data")
            ff_m.append(df['ff_m'].values)
            ff_c.append(df['ff_c'].values)
    ff_m = np.array(ff_m)
    ff_c = np.array(ff_c)

    p_m = ScatterPlotter()
    p_m.plot(nsb, ff_m)
    p_m.save(get_plot("ff_m_versus_nsb.pdf"))

    p_c = ScatterPlotter()
    p_c.plot(nsb, ff_c)
    p_c.save(get_plot("ff_c_versus_nsb.pdf"))


def main():
    nsb = np.array([[0]*2048, [5]*2048, [40]*2048, [1200]*2048])
    paths = [
        "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/0mhz/ff_coefficients.h5",
        "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/5mhz/ff_coefficients.h5",
        "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/40mhz/ff_coefficients.h5",
        "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/1200mhz/ff_coefficients.h5",
    ]
    process(paths, nsb)


if __name__ == '__main__':
    main()

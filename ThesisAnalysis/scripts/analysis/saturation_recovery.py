from ThesisAnalysis import ThesisHDF5Writer, ThesisHDF5Reader, get_data, get_plot
from ThesisAnalysis.plotting.setup import ThesisPlotter
import numpy as np
import pandas as pd
import os
from numpy.polynomial.polynomial import polyfit
from matplotlib.colors import LogNorm
from matplotlib.ticker import FuncFormatter


class ScatterPlotter(ThesisPlotter):
    def plot(self, x, y, yerr):

        (_, caps, _) = self.ax.errorbar(x, y, yerr=yerr,
                                        fmt='o', mew=1,
                                        markersize=3, capsize=3,
                                        elinewidth=0.7, label="")
        for cap in caps:
            cap.set_markeredgewidth(0.7)

        self.ax.set_xscale('log')
        self.ax.get_xaxis().set_major_formatter(
            FuncFormatter(lambda xl, _: '{:g}'.format(xl)))

        self.ax.set_yscale('log')
        self.ax.get_yaxis().set_major_formatter(
            FuncFormatter(lambda yl, _: '{:g}'.format(yl)))

        self.ax.set_xlabel("Expected Charge (p.e.)")
        self.ax.set_ylabel("Saturation Coefficient (mV ns)")


def process(input_path, poi):

    with ThesisHDF5Reader(input_path) as reader:
        df = reader.read("data")

    df = df.loc[df['pixel'] == poi]

    x = df['amplitude'].values
    y = df['mean'].values
    yerr = df['std'].values

    output_dir = os.path.dirname(input_path)

    p_scatter = ScatterPlotter()
    p_scatter.plot(x, y, yerr)
    p_scatter.save(get_plot("saturation_recovery.pdf"))


def main():
    input_path = get_data("saturation_recovery.h5")
    poi = 888
    process(input_path, poi)


if __name__ == '__main__':
    main()

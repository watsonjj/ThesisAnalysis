from ThesisAnalysis import get_data, ThesisHDF5Reader, get_plot
from ThesisAnalysis.plotting.setup import ThesisPlotter
import os
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from CHECLabPy.core.io import DL1Reader
from CHECLabPy.spectrum_fitters.gentile import GentileFitter
from IPython import embed


class SPEPlotter(ThesisPlotter):
    def plot(self, df):
        for _, row in df.iterrows():
            type_ = row['type']
            norm = row['norm{}'.format(row['roi'])]
            edges = row['edges']
            between = row['between']
            fitx = row['fitx']
            lambda_ = row['lambda_{}'.format(row['roi'])]
            hist = row['hist'] / norm
            fit = row['fit'] / norm

            color = next(self.ax._get_lines.prop_cycler)['color']
            self.ax.hist(between, bins=edges, weights=hist, histtype='step',
                         color=color)
            self.ax.plot(fitx, fit, color=color,
                         label="{} ({:.3f} p.e.)".format(type_, lambda_))

        self.add_legend()
        self.ax.set_xlabel("Charge (p.e.)")
        self.ax.set_ylabel("Count Percentage")


class SPEPlotterTable(SPEPlotter):
    def __init__(self):
        super().__init__()

        self.fig = plt.figure(figsize=self.get_figsize())
        self.ax = plt.subplot2grid((3, 2), (0, 0), rowspan=3)
        self.ax_t = plt.subplot2grid((3, 2), (0, 1), rowspan=3)

    def plot(self, df):
        super().plot(df)

        type_list = []
        coeff_list = []
        for _, row in df.iterrows():
            type_ = row['type']
            spe = row['spe']
            coeff = dict(
                lambda_0=row['lambda_0'],
                lambda_1=row['lambda_1'],
                lambda_2=row['lambda_2'],
                eped=row['eped']/spe,
                eped_sigma=row['eped_sigma']/spe,
                spe=1,
                spe_sigma=row['spe_sigma']/spe,
                opct=row['opct'],
            )
            type_list.append(type_)
            coeff_list.append(coeff)

        self.ax_t.axis('off')
        columns = [*type_list]
        rows = list(coeff_list[0].keys())
        cells = [['%.3g' % coeff_list[0][i], '%.3g' % coeff_list[1][i]] for i in rows]
        table = self.ax_t.table(cellText=cells, rowLabels=rows,
                                colLabels=columns, loc='center')
        table.set_fontsize(10)


def process(path):
    with ThesisHDF5Reader(path) as reader:
        df = reader.read("data")

    p_spe = SPEPlotter()
    p_spe.plot(df)
    p_spe.save(get_plot("spe_spectrum/spe_comparison.pdf"))

    p_spe_table = SPEPlotterTable()
    p_spe_table.plot(df)
    p_spe_table.save(get_plot("spe_spectrum/spe_comparison_table.pdf"))


def main():
    path = get_data("spe_spectrum_comparison.h5")
    process(path)


if __name__ == '__main__':
    main()
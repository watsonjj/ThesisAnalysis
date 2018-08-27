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
    def plot(self, n_illuminations, df_array, df_coeff):
        coeff = df_coeff.iloc[0].to_dict()
        edges = df_array.iloc[0]['edges']
        between = df_array.iloc[0]['between']
        fitx = df_array.iloc[0]['fitx']

        for i in range(n_illuminations):
            color = next(self.ax._get_lines.prop_cycler)['color']
            lambda_ = coeff['lambda_{}'.format(i)]
            hist = df_array.iloc[0]['hist{}'.format(i)]
            fit = df_array.iloc[0]['fit{}'.format(i)]

            self.ax.hist(between, bins=edges, weights=hist, histtype='step',
                         color=color)
            self.ax.plot(fitx, fit, color=color,
                         label="{:.3f} p.e.".format(lambda_))

        self.add_legend()
        self.ax.set_xlabel("Charge (mV ns)")
        self.ax.set_ylabel("N")


class SPEPlotterTable(SPEPlotter):
    def __init__(self):
        super().__init__()

        self.fig = plt.figure(figsize=self.get_figsize())
        self.ax = plt.subplot2grid((3, 2), (0, 0), rowspan=3)
        self.ax_t = plt.subplot2grid((3, 2), (0, 1), rowspan=3)

    def plot(self, n_illuminations, df_array, df_coeff):
        super().plot(n_illuminations, df_array, df_coeff)

        coeff = df_coeff.iloc[0].to_dict()

        self.ax_t.axis('off')
        columns = ['Fit Coeff']
        rows = list(coeff.keys())
        cells = [['%.3g' % coeff[i]] for i in rows]
        table = self.ax_t.table(cellText=cells, rowLabels=rows,
                                colLabels=columns, loc='center')
        table.set_fontsize(10)


def process(input_path):
    with ThesisHDF5Reader(input_path) as reader:
        df_array = reader.read("array")
        df_coeff = reader.read("coeff")
        mapping = reader.read_mapping()
        metadata = reader.read_metadata()

    n_illuminations = metadata['n_illuminations']

    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_dir = get_plot("spe_spectrum")

    p_spe = SPEPlotter()
    p_spe.plot(n_illuminations, df_array, df_coeff)
    p_spe.save(os.path.join(output_dir, base_name+".pdf"))

    p_spe_table = SPEPlotterTable()
    p_spe_table.plot(n_illuminations, df_array, df_coeff)
    p_spe_table.save(os.path.join(output_dir, base_name+"_table.pdf"))


def main():
    input_path = get_data("spe/mc_spe_spectrum.h5")
    process(input_path)

    input_path = get_data("spe/lab_tfnone_spe_spectrum.h5")
    process(input_path)

    input_path = get_data("spe/lab_tfpchip_spe_spectrum.h5")
    process(input_path)

    input_path = get_data("spe/lab_tfpoly_spe_spectrum.h5")
    process(input_path)

    input_path = get_data("spe/lab_tfwithped_spe_spectrum.h5")
    process(input_path)

    input_path = get_data("spe/lab_50ADC_spe_spectrum.h5")
    process(input_path)

    input_path = get_data("spe/lab_100ADC_spe_spectrum.h5")
    process(input_path)

    input_path = get_data("spe/lab_200ADC_spe_spectrum.h5")
    process(input_path)

    input_path = get_data("spe/checm_spe_spectrum.h5")
    process(input_path)


if __name__ == '__main__':
    main()
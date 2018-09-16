from ThesisAnalysis.plotting.setup import ThesisPlotter
from ThesisAnalysis import ThesisHDF5Reader, get_data, get_plot
import numpy as np
from matplotlib.ticker import FuncFormatter
from IPython import embed


def sum_errors(array):
    return np.sqrt(np.sum(np.power(array, 2)) / array.size)


class PulseShapePlotter(ThesisPlotter):
    def plot(self, x, tr, fwhm, xerr, tr_err, fwhm_err):
        (_, caps, _) = self.ax.errorbar(
            x, fwhm, xerr=xerr, yerr=fwhm_err, mew=1, capsize=1, elinewidth=0.5,
            markersize=2, label="FWHM", linewidth=0.5, fmt='.',
        )
        for cap in caps:
            cap.set_markeredgewidth(0.5)

        (_, caps, _) = self.ax.errorbar(
            x, tr, xerr=xerr, yerr=tr_err, mew=1, capsize=1, elinewidth=0.5,
            markersize=2, label="Rise Time", linewidth=0.5, fmt='.',
        )
        for cap in caps:
            cap.set_markeredgewidth(0.5)

        self.ax.set_xscale('log')
        self.ax.get_xaxis().set_major_formatter(
            FuncFormatter(lambda x, _: '{:g}'.format(x)))
        # self.ax.set_yscale('log')
        # self.ax.get_yaxis().set_major_formatter(
        #     FuncFormatter(lambda y, _: '{:g}'.format(y)))

        self.ax.set_xlabel("Average Expected Charge (p.e.)")
        self.ax.set_ylabel("Time (ns)")
        self.add_legend(5)


def process(input_path, output_path):
    with ThesisHDF5Reader(input_path) as reader:
        df = reader.read("data")

    df_gr = df.groupby('expected')
    df_mean = df_gr.mean()
    df_std = df_gr.std()
    df_err = df_gr.apply(sum_errors)
    x = df_mean.index
    tr = df_mean['tr'].values
    fwhm = df_mean['fwhm'].values
    xerr = df_err['expected_err'].values
    tr_err = df_std['tr'].values
    fwhm_err = df_std['fwhm'].values

    p_pulseshape = PulseShapePlotter()
    p_pulseshape.plot(x, tr, fwhm, xerr, tr_err, fwhm_err)
    p_pulseshape.save(output_path)


def main():
    input_path = get_data("pulse_shape/pulse_shape_lab.h5")
    output_path = get_plot("pulse_shape/pulse_shape_lab.pdf")
    process(input_path, output_path)

    input_path = get_data("pulse_shape/pulse_shape_mc.h5")
    output_path = get_plot("pulse_shape/pulse_shape_mc.pdf")
    process(input_path, output_path)

    input_path = get_data("pulse_shape/pulse_shape_checm.h5")
    output_path = get_plot("pulse_shape/pulse_shape_checm.pdf")
    process(input_path, output_path)

    input_path = get_data("pulse_shape/pulse_shape_tfwf.h5")
    output_path = get_plot("pulse_shape/pulse_shape_tfwf.pdf")
    process(input_path, output_path)


if __name__ == '__main__':
    main()
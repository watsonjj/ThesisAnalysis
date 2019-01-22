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


class ChargePlotter(ThesisPlotter):
    def plot(self, x, charge, charge_cc, xerr, charge_err, charge_cc_err):
        (_, caps, _) = self.ax.errorbar(
            x, charge, xerr=xerr, yerr=charge_err, mew=1, capsize=1,
            elinewidth=0.5,
            markersize=2, label="Window Integrator", linewidth=0.5, fmt='.',
        )
        for cap in caps:
            cap.set_markeredgewidth(0.5)

        (_, caps, _) = self.ax.errorbar(
            x, charge_cc, xerr=xerr, yerr=charge_cc_err, mew=1, capsize=1,
            elinewidth=0.5,
            markersize=2, label="Cross Correlation", linewidth=0.5, fmt='.',
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
        self.ax.set_ylabel("Charge Extractrated from Normalised Waveform")
        self.add_legend('best')


def process(input_path, output_path1, output_path2):
    with ThesisHDF5Reader(input_path) as reader:
        df = reader.read("data")

    df = df.loc[df['expected'] > 0.3]
    df_gr = df.groupby('expected')
    df_mean = df_gr.mean()
    df_std = df_gr.std()
    df_err = df_gr.apply(sum_errors)
    x = df_mean.index
    tr = df_mean['tr'].values
    fwhm = df_mean['fwhm'].values
    charge = df_mean['charge'].values
    charge_cc = df_mean['charge_cc'].values
    xerr = df_err['expected_err'].values
    tr_err = df_std['tr'].values
    fwhm_err = df_std['fwhm'].values
    charge_err = df_std['charge'].values
    charge_cc_err = df_std['charge_cc'].values

    i50 = np.argmin(np.abs(x - 50))
    charge /= charge[i50]
    charge_err /= charge[i50]
    charge_cc /= charge_cc[i50]
    charge_cc_err /= charge_cc[i50]

    p_pulseshape = PulseShapePlotter()
    p_pulseshape.plot(x, tr, fwhm, xerr, tr_err, fwhm_err)
    p_pulseshape.save(output_path1)

    p_charge = ChargePlotter()
    p_charge.plot(x, charge, charge_cc, xerr, charge_err, charge_cc_err)
    p_charge.save(output_path2)


def main():
    input_path = get_data("cc_pulse_shape/pulse_shape_lab.h5")
    output_path1 = get_plot("cc_pulse_shape/pulse_shape_lab.pdf")
    output_path2 = get_plot("cc_pulse_shape/pulse_shape_lab_charge.pdf")
    process(input_path, output_path1, output_path2)


if __name__ == '__main__':
    main()
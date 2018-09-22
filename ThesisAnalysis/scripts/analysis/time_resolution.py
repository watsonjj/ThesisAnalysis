from ThesisAnalysis.plotting.setup import ThesisPlotter
from ThesisAnalysis import ThesisHDF5Reader, get_data, get_plot
import numpy as np
from matplotlib.ticker import FuncFormatter
from IPython import embed


def sum_errors(array):
    return np.sqrt(np.sum(np.power(array, 2)) / array.size)


class TimeResPlotter(ThesisPlotter):
    def plot(self, x, y, xerr, yerr, label=""):

        (_, caps, _) = self.ax.errorbar(
            x, y, xerr=xerr, yerr=yerr, mew=1, capsize=1, elinewidth=0.5,
            markersize=2, label=label, linewidth=0.5, fmt='.',
        )
        for cap in caps:
            cap.set_markeredgewidth(0.5)

        self.ax.set_xscale('log')
        self.ax.get_xaxis().set_major_formatter(
            FuncFormatter(lambda x, _: '{:g}'.format(x)))
        # self.ax.set_yscale('log')
        # self.ax.get_yaxis().set_major_formatter(
        #     FuncFormatter(lambda y, _: '{:g}'.format(y)))

    def plot_from_path(self, input_path, label=""):
        with ThesisHDF5Reader(input_path) as reader:
            df = reader.read("data")

            embed()

        df_gb = df.groupby("expected")
        df_mean = df_gb.mean()
        df_std = df_gb.std()

        x = df_mean.index.values
        y = df_mean['std'].values
        xerr = df_mean['expected_err'].values
        yerr = df_std['std'].values

        self.plot(x, y, xerr, yerr, label)

    def finish(self):
        # xmin, xmax = self.ax.get_xlim()
        # x = [5, xmax]
        # y = [2, 2]
        # self.ax.plot(x, y, '--', color='black', label="Requirement")
        # self.ax.set_xlim(xmin, xmax)
        self.ax.axhline(2, ls='--', color='black', label="Requirement")
        self.ax.set_xlabel("Average Expected Charge (p.e.)")
        self.ax.set_ylabel("Time Resolution (ns)")
        self.add_legend("best")


def process():
    output_path = get_plot("time_resolution/checs.pdf")
    p = TimeResPlotter()
    p.plot_from_path(get_data("time_resolution/lab.h5"), "Lab")
    p.plot_from_path(get_data("time_resolution/mc.h5"), "Simulation")
    p.plot_from_path(get_data("time_resolution/mc125.h5"), "Simulation, 125MHz")
    p.save(output_path)

    output_path = get_plot("time_resolution/checm.pdf")
    p = TimeResPlotter()
    p.plot_from_path(get_data("time_resolution/checm.h5"))
    p.save(output_path)


def main():
    process()

if __name__ == '__main__':
    main()
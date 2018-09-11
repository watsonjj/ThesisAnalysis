from ThesisAnalysis import ThesisHDF5Reader
from ThesisAnalysis.files import all_files
from ThesisAnalysis.plotting.setup import ThesisPlotter
import numpy as np
import os
from matplotlib.colors import LogNorm
from matplotlib.ticker import FuncFormatter


class FitPlotter(ThesisPlotter):
    def plot(self, x, y, yerr, flag, c, m):

        x_fit = np.geomspace(0.1, 1000, 1000)
        y_fit = m * x_fit

        (_, caps, _) = self.ax.errorbar(x[~flag], y[~flag], yerr=yerr[~flag],
                                        fmt='o', mew=1,
                                        markersize=3, capsize=3,
                                        elinewidth=0.7, label="")
        for cap in caps:
            cap.set_markeredgewidth(0.7)

        color = self.ax._get_lines.get_next_color()
        self.ax.plot(x_fit, y_fit, color=color, label="Linear Regression")

        (_, caps, _) = self.ax.errorbar(x[flag], y[flag], yerr=yerr[flag],
                                        fmt='o', mew=1, color=color,
                                        markersize=3, capsize=3,
                                        elinewidth=0.7,
                                        label="Regressed Points")
        for cap in caps:
            cap.set_markeredgewidth(0.7)

        self.ax.set_xscale('log')
        self.ax.get_xaxis().set_major_formatter(
            FuncFormatter(lambda xl, _: '{:g}'.format(xl)))

        self.ax.set_yscale('log')
        self.ax.get_yaxis().set_major_formatter(
            FuncFormatter(lambda yl, _: '{:g}'.format(yl)))

        self.ax.set_xlabel("Average Expected Charge (p.e.)")
        self.ax.set_ylabel("Average Measured Charge (mV)")
        self.add_legend('best')


class Hist2D(ThesisPlotter):
    def plot(self, x, y):
        xbins = np.geomspace(x[x > 0].min(), x.max(), 100)
        ybins = np.geomspace(y[y > 0].min(), y.max(), 100)

        hist, xedges, yedges = np.histogram2d(x.ravel(), y.ravel(),
                                              bins=(xbins, ybins))
        hist = np.ma.masked_where(hist == 0, hist)
        z = hist
        norm = LogNorm(vmin=hist.min(), vmax=hist.max())
        im = self.ax.pcolormesh(xedges, yedges, z.T, cmap="viridis",
                                edgecolors='white', linewidths=0, norm=norm)
        cbar = self.fig.colorbar(im)

        self.ax.set_xscale('log')
        self.ax.get_xaxis().set_major_formatter(
            FuncFormatter(lambda xl, _: '{:g}'.format(xl)))

        self.ax.set_yscale('log')
        self.ax.get_yaxis().set_major_formatter(
            FuncFormatter(lambda yl, _: '{:g}'.format(yl)))

        self.ax.set_xlabel("Average Expected Charge (p.e.)")
        self.ax.set_ylabel("Average Measured Charge (mV)")
        cbar.set_label("N")


def process(file):
    charge_resolution_path = file.charge_resolution_path

    with ThesisHDF5Reader(charge_resolution_path) as reader:
        df = reader.read("charge_statistics_pixel")

    true = df['amplitude'].values
    mean = df['mean'].values

    output_dir = os.path.dirname(charge_resolution_path)

    p_hist2d = Hist2D()
    p_hist2d.plot(true, mean)
    p_hist2d.save(os.path.join(output_dir, "ff_charge_average_hist2D.pdf"))


def main():
    [process(f) for f in all_files]


if __name__ == '__main__':
    main()

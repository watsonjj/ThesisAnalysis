from ThesisAnalysis import ThesisHDF5Reader, get_data, get_plot
from ThesisAnalysis.plotting.setup import ThesisPlotter
import numpy as np
from matplotlib.colors import LogNorm
from matplotlib.ticker import FuncFormatter


class Hist2D(ThesisPlotter):
    def plot(self, df):
        x = df['true'].values
        y = df['measured'].values

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

        xu = np.unique(x)
        self.ax.plot(x, x, ':', color='grey')

        self.ax.set_xscale('log')
        self.ax.get_xaxis().set_major_formatter(
            FuncFormatter(lambda xl, _: '{:g}'.format(xl)))

        self.ax.set_yscale('log')
        self.ax.get_yaxis().set_major_formatter(
            FuncFormatter(lambda yl, _: '{:g}'.format(yl)))

        self.ax.set_xlabel("Average Expected Charge (p.e.)")
        self.ax.set_ylabel("Average Measured Charge (p.e.)")
        cbar.set_label("N")


class ScatterPlotter(ThesisPlotter):
    def plot(self, df):

        df_mean = df.groupby('true').mean()
        df_std = df.groupby('true').std()

        x = df_mean.index.values
        y = df_mean['measured'].values
        xerr = np.sqrt(x)
        yerr = df_std['measured'].values

        (_, caps, _) = self.ax.errorbar(x, y, xerr=xerr, yerr=yerr,
                                        fmt='o', mew=1,
                                        markersize=3, capsize=3,
                                        elinewidth=0.7, color='black',
                                        zorder=1)
        for cap in caps:
            cap.set_markeredgewidth(0.7)

        self.ax.plot(x, x, ':', color='grey', zorder=2)

        self.ax.set_xscale('log')
        self.ax.get_xaxis().set_major_formatter(
            FuncFormatter(lambda xl, _: '{:g}'.format(xl)))
        self.ax.set_yscale('log')
        self.ax.get_yaxis().set_major_formatter(
            FuncFormatter(lambda yl, _: '{:g}'.format(yl)))

        self.ax.set_xlabel("Average Expected Charge (p.e.)")
        self.ax.set_ylabel("Average Measured Charge (p.e.)")


def process(input_file, hist_path, scatter_path):

    with ThesisHDF5Reader(input_file) as reader:
        df = reader.read("data")
    #
    # p_hist = Hist2D()
    # p_hist.plot(df)
    # p_hist.save(hist_path)

    p_scatter = ScatterPlotter()
    p_scatter.plot(df)
    p_scatter.save(scatter_path)


def main():
    input_path = get_data("measured_vs_expected/measured_vs_expected_checs.h5")
    hist_path = get_plot("measured_vs_expected/checs/measured_vs_expected_hist.pdf")
    scatter_path = get_plot("measured_vs_expected/checs/measured_vs_expected_scatter.pdf")
    process(input_path, hist_path, scatter_path)

    input_path = get_data("measured_vs_expected/measured_vs_expected_checm.h5")
    hist_path = get_plot("measured_vs_expected/checm/measured_vs_expected_hist.pdf")
    scatter_path = get_plot("measured_vs_expected/checm/measured_vs_expected_scatter.pdf")
    process(input_path, hist_path, scatter_path)


if __name__ == '__main__':
    main()

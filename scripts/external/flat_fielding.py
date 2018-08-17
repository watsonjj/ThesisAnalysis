from ThesisAnalysis import ThesisHDF5Writer, ThesisHDF5Reader
from ThesisAnalysis.plotting.setup import ThesisPlotter
import numpy as np
import pandas as pd
import os
from numpy.polynomial.polynomial import polyfit
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

        self.ax.set_xlabel("Expected Charge (p.e.)")
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

        self.ax.set_xlabel("Expected Charge (p.e.)")
        self.ax.set_ylabel("Average Measured Charge (mV)")
        cbar.set_label("N")


def process(input_path, fw_path, poi):

    with ThesisHDF5Reader(input_path) as reader:
        df_avg = reader.read("data")
        mapping = reader.read_mapping()
        metadata = reader.read_metadata()

    with ThesisHDF5Reader(fw_path) as reader:
        df_fw = reader.read("data")

    pixel = df_avg['pixel'].values
    transmission = df_avg['transmission'].values
    fw_m = df_fw['fw_m'].values
    df_avg['illumination'] = transmission * fw_m[pixel]

    pe_expected = df_avg['pe_expected']
    df_avg['flag'] = ((pe_expected >= 45) & (pe_expected <= 60))

    output_dir = os.path.dirname(input_path)

    d_list = []
    for pix in np.unique(df_avg['pixel']):
        # if pix != poi:
        #     continue

        df_p = df_avg.loc[df_avg['pixel'] == pix]
        true = df_p['illumination'].values
        measured = df_p['mean'].values
        measured_std = df_p['std'].values
        flag = df_p['flag'].values

        true_f = true[flag]
        measured_f = measured[flag]
        measured_std_f = measured_std[flag]

        ff_c, ff_m = polyfit(true_f, measured_f, [1], w=1 / measured_std_f)
        d_list.append(dict(
            pixel=pix,
            ff_c=ff_c,
            ff_m=ff_m
        ))

        if pix == poi:
            p_fit = FitPlotter()
            p_fit.plot(true, measured, measured_std, flag, ff_c, ff_m)
            p_fit.save(os.path.join(output_dir, "flat_fielding.pdf"))

    df_calib = pd.DataFrame(d_list)
    df_calib = df_calib.sort_values('pixel')
    path = os.path.join(output_dir, "ff_coefficients.h5")
    with ThesisHDF5Writer(path) as writer:
        writer.write(data=df_calib)
        writer.write_mapping(mapping)
        writer.write_metadata(**metadata)

    p_hist2d = Hist2D()
    p_hist2d.plot(df_avg['illumination'].values, df_avg['mean'].values)
    p_hist2d.save(os.path.join(output_dir, "pixel_averages.pdf"))


def main():
    poi = 888

    fw_path = "/Users/Jason/Software/ThesisAnalysis/ThesisAnalysis/data/mc_fw_calibration.h5"
    paths = [
        "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/0mhz/charge_averages.h5",
        "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/5mhz/charge_averages.h5",
        "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/40mhz/charge_averages.h5",
        "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/1200mhz/charge_averages.h5",
    ]
    for p in paths:
        process(p, fw_path, poi)

    fw_path = "/Users/Jason/Software/ThesisAnalysis/ThesisAnalysis/data/lab_tfnone_fw_calibration.h5"
    averages_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_none/charge_averages.h5"
    process(averages_path, fw_path, poi)

    fw_path = "/Users/Jason/Software/ThesisAnalysis/ThesisAnalysis/data/lab_tfpchip_fw_calibration.h5"
    averages_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_pchip/charge_averages.h5"
    process(averages_path, fw_path, poi)

    fw_path = "/Users/Jason/Software/ThesisAnalysis/ThesisAnalysis/data/lab_tfpoly_fw_calibration.h5"
    averages_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_poly/charge_averages.h5"
    process(averages_path, fw_path, poi)

    fw_path = "/Users/Jason/Software/ThesisAnalysis/ThesisAnalysis/data/lab_tfwithped_fw_calibration.h5"
    averages_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_withped/charge_averages.h5"
    process(averages_path, fw_path, poi)


if __name__ == '__main__':
    main()

from ThesisAnalysis import get_data, get_plot, ThesisHDF5Reader
from ThesisAnalysis.plotting.setup import ThesisPlotter
from ThesisAnalysis.files import Lab_TFPoly
from CHECLabPy.utils.files import read_runlist
from matplotlib.ticker import FuncFormatter
from numpy.polynomial.polynomial import polyfit, polyval
import numpy as np
from IPython import embed


class LinePlotterRunlist(ThesisPlotter):
    def plot(self, x, y):
        self.ax.plot(x, y, 'o', color='black', ms=0.5)

        self.ax.set_xlabel("Filter Wheel Position")
        self.ax.set_ylabel("Filter Wheel Transmission")
        self.ax.set_yscale('log')
        self.ax.get_yaxis().set_major_formatter(
            FuncFormatter(lambda y, _: '{:g}'.format(y)))

        self.ax.axhline(y[40], ls='--')
        self.ax.axhline(y[49], ls='--')

        yl = np.log10(y)
        v1 = polyfit(x[:41], yl[:41], 1)
        v2 = polyfit(x[41:50], yl[41:50], 1)
        v3 = polyfit(x[50:], yl[50:], 1)

        # xf = np.linspace(x.min(), x.max(), 100)
        self.ax.plot(x, 10**polyval(x, v1), alpha=0.2)
        self.ax.plot(x, 10**polyval(x, v2), alpha=0.2)
        self.ax.plot(x, 10**polyval(x, v3), alpha=0.2)


class LinePlotterJustus(ThesisPlotter):
    def plot(self, x, y, yerr):
        # self.ax.plot(x, y, 'o', color='black', ms=0.5)

        print(x.min(), x.max())

        f1 = x <= 1500
        f2 = (x > 1500) & (x <= 1850)
        f3 = x > 1850
        x1 = x[f1]
        x2 = x[f2]
        x3 = x[f3]
        y1 = y[f1]
        y2 = y[f2]
        y3 = y[f3]
        yerr1 = yerr[f1]
        yerr2 = yerr[f2]
        yerr3 = yerr[f3]
        label1 = "SiPM with Pre-amplifier (Photoelectron Counting)"
        label2 = "SiPM with Pre-amplifier"
        label3 = "SiPM without Pre-amplifier"

        (_, caps, _) = self.ax.errorbar(x1, y1, yerr=yerr1,
                                        fmt='o', mew=1,
                                        markersize=1, capsize=3,
                                        elinewidth=0.7, label=label1, zorder=1)
        for cap in caps:
            cap.set_markeredgewidth(0.7)


        (_, caps, _) = self.ax.errorbar(x2, y2, yerr=yerr2,
                                        fmt='o', mew=1,
                                        markersize=1, capsize=3,
                                        elinewidth=0.7, label=label2, zorder=1)
        for cap in caps:
            cap.set_markeredgewidth(0.7)



        (_, caps, _) = self.ax.errorbar(x3, y3, yerr=yerr3,
                                        fmt='o', mew=1,
                                        markersize=1, capsize=3,
                                        elinewidth=0.7, label=label3, zorder=1)
        for cap in caps:
            cap.set_markeredgewidth(0.7)


        # yl = np.log10(y)
        # yerrl = np.log10(yerr)
        # v = polyfit(x, yl, 1, w=1/yerrl)
        # self.ax.plot(x, 10 ** polyval(x, v), alpha=0.9, zorder=2,
        #              label=r"$\text{{Transmission}} = 10^{{{:.3g} \times \text{{Position}} {:+.3g}}}$".format(v[1], v[0]))

        # self.ax.plot(x, y, zorder=2)

        self.ax.set_xlabel("Filter-Wheel Position")
        self.ax.set_ylabel("Filter-Wheel Transmission")
        self.ax.set_yscale('log')
        self.ax.get_yaxis().set_major_formatter(
            FuncFormatter(lambda y, _: '{:g}'.format(y)))
        self.add_legend("best")


def process_runlist(input_path, output_path, output_path_pe, fw_path, poi):

    df = read_runlist(input_path)
    df['transmission'] = 1 / df['fw_atten']

    with ThesisHDF5Reader(fw_path) as reader:
        df_fwc = reader.read("data")
        fw_m = df_fwc['fw_m'].values

    x = df['fw_pos'].values
    y = df['transmission'].values
    y_pe = y * fw_m[poi]

    p_line = LinePlotterRunlist()
    p_line.plot(x, y)
    p_line.save(output_path)

    p_line_pe = LinePlotterRunlist()
    p_line_pe.plot(x, y_pe)
    p_line_pe.ax.set_ylabel("Illumination Amplitude (p.e.)")
    p_line_pe.save(output_path_pe)


def process_justus_txt(input_path, output_path):
    x, y, yerr = np.loadtxt(input_path, unpack=True)

    # flag = x > 1500
    x = x[:-3]
    y = y[:-3]
    yerr = yerr[:-3]

    p_line = LinePlotterJustus()
    p_line.plot(x, y, yerr)
    p_line.save(output_path)

    # embed()

def main():
    file = Lab_TFPoly()
    input_path = file.runlist_path
    fw_path = file.fw_path
    output_path = get_plot("fw_position/runlist.pdf")
    output_path_pe = get_plot("fw_position/runlist_pe.pdf")
    poi = 888
    process_runlist(input_path, output_path, output_path_pe, fw_path, poi)

    input_path = get_data("transmission_combined_d2018-02-07-and_d2017-08-17.txt")
    output_path = get_plot("fw_position/fw_position_justus.pdf")
    process_justus_txt(input_path, output_path)


if __name__ == '__main__':
    main()

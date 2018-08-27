from ThesisAnalysis.plotting.setup import ThesisPlotter
from ThesisAnalysis import get_plot, ThesisHDF5Reader
from ThesisAnalysis.files import *
from matplotlib.ticker import FuncFormatter
import numpy as np
import pandas as pd
from numpy.polynomial.polynomial import polyfit, polyval


def remove_dead_pixels(df, dead):
    return df.loc[~df['pixel'].isin(dead)]


def get_df_camera_stats(df, groupby="camera_expected"):
    df_mean = df.groupby(groupby).mean()
    df_std = df.groupby(groupby).std()
    return df_mean, df_std


class ScatterPlotter(ThesisPlotter):
    def __init__(self, xlabel, ylabel, **kwargs):
        super().__init__(**kwargs)
        self.xlabel = xlabel
        self.ylabel = ylabel

    def plot(self, x, y, yerr=None, label="", **kwargs):
        (_, caps, _) = self.ax.errorbar(x, y, yerr=yerr,
                                        fmt='o', mew=1,
                                        markersize=3, capsize=3,
                                        elinewidth=0.7, label=label,
                                        **kwargs)
        for cap in caps:
            cap.set_markeredgewidth(0.7)

    def set_log_x(self):
        self.ax.set_xscale('log')
        self.ax.get_xaxis().set_major_formatter(
            FuncFormatter(lambda xl, _: '{:g}'.format(xl)))

    def set_log_y(self):
        self.ax.set_yscale('log')
        self.ax.get_yaxis().set_major_formatter(
            FuncFormatter(lambda yl, _: '{:g}'.format(yl)))

    def finish(self):
        self.ax.set_xlabel(self.xlabel)
        self.ax.set_ylabel(self.ylabel)


def process(file_dict, subdir):
    e = 22
    s = np.s_[e:37]

    output_dir = get_plot("fw_correction/{}".format(subdir))

    output_path = os.path.join(output_dir, "measured_versus_transmission.pdf")
    xlabel = "Filter-Wheel Transmission"
    ylabel = "Measured Charge (mV ns)"
    p_scatter = ScatterPlotter(xlabel, ylabel)
    for l, file in file_dict.items():
        with ThesisHDF5Reader(file.charge_before_after_path) as r:
            df = r.read('data')
        dead = file.dead
        df = remove_dead_pixels(df, dead)
        df_mean, df_std = get_df_camera_stats(df, "transmission")
        x = df_mean.index
        y = df_mean['before_mVns_ip'].values
        yerr = df_std['before_mVns_ip'].values

        c, m = polyfit(x[s], y[s], [1], w=1/yerr[s])

        yf = polyval(x, (c, m))

        color = p_scatter.ax._get_lines.get_next_color()
        p_scatter.plot(x, y, yerr, l, color=color)
        p_scatter.ax.plot(x, yf, color=color, label="")
    p_scatter.set_log_x()
    p_scatter.set_log_y()
    p_scatter.add_legend('best')
    p_scatter.save(output_path)

    output_path = os.path.join(output_dir, "fw_correction.pdf")
    xlabel = "Filter-Wheel Position"
    ylabel = "Effective Transmission"
    p_scatter = ScatterPlotter(xlabel, ylabel)
    fit_points_x = []
    fit_points_y = []
    fit_points_yerr = []
    for l, file in file_dict.items():
        with ThesisHDF5Reader(file.charge_before_after_path) as r:
            df = r.read('data')
        dead = file.dead
        df = remove_dead_pixels(df, dead)
        df_mean, df_std = get_df_camera_stats(df, "transmission")
        transmission = df_mean.index
        fw_pos = df_mean['fw_pos'].values
        charge = df_mean['before_mVns_ip'].values
        charge_std = df_std['before_mVns_ip'].values

        c, m = polyfit(transmission[s], charge[s], [1])

        eff_transmission = charge / m
        eff_transmission_std = charge_std / m

        fit_points_x.append(fw_pos)
        fit_points_y.append(eff_transmission)
        fit_points_yerr.append(eff_transmission_std)

        p_scatter.plot(fw_pos, eff_transmission, eff_transmission_std, l,
                       zorder=1)
    x = np.array(fit_points_x)
    y = np.array(fit_points_y)
    yerr = np.array(fit_points_yerr)
    ylog = np.log10(y[:, s])
    yerrlog = yerr[:, s] / (y[:, s] * np.log(10))
    c, m = polyfit(x[:, s].ravel(), ylog.ravel(), 1, w=1/yerrlog.ravel())
    xf = np.unique(x)
    yf = 10 ** polyval(xf, (c, m))
    yf[:e] = np.mean(y[:, :e], 0)
    p_scatter.ax.plot(xf, yf, color='black', zorder=2, label="Fit")
    p_scatter.set_log_y()
    p_scatter.add_legend('best')
    p_scatter.save(output_path)

    input_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/runlist_original.txt"
    output_path = os.path.join(output_dir, "runlist_new.txt")
    yf = 10 ** (np.log10(yf) - np.log10(yf[-1]))
    assert yf[-1] == 1
    df = pd.read_csv(input_path, sep=' ')
    pe = df.iloc[0]['pe_expected'] * df.iloc[0]['fw_atten']
    df['fw_trans'] = yf[::-1]
    df['fw_atten'] = 1 / yf[::-1]
    df['pe_expected'] = pe / df['fw_atten']
    df.to_csv(output_path, sep=' ', float_format="%.5f", index=False)
    print("New runlist created: {}".format(output_path))


def main():
    file_dict = {
        "50ADC-GM": Lab_GM50ADC_Original(),
        "100ADC-GM": Lab_GM100ADC_Original(),
        "200ADC-GM": Lab_GM200ADC_Original(),
    }
    subdir = "gain-matching-original"
    process(file_dict, subdir)

    file_dict = {
        "50ADC-GM": Lab_GM50ADC(),
        "100ADC-GM": Lab_GM100ADC(),
        "200ADC-GM": Lab_GM200ADC(),
    }
    subdir = "gain-matching-post"
    process(file_dict, subdir)

    file_dict = {
        "TF-None": Lab_TFNone(),
        "TF-Poly": Lab_TFPoly(),
        "TF-Pchip": Lab_TFPchip(),
        "TF-WithPed": Lab_TFWithPed(),
    }
    subdir = "tf-comparison"
    process(file_dict, subdir)


if __name__ == '__main__':
    main()

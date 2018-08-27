from ThesisAnalysis.plotting.setup import ThesisPlotter
from ThesisAnalysis import get_plot, ThesisHDF5Reader
from ThesisAnalysis.files import *
from matplotlib.ticker import FuncFormatter
from numpy.polynomial.polynomial import polyfit


# class Violin(ThesisPlotter):
#     def plot(self, df):
#
#         camera_expected = df['camera_expected'].values
#         before_ip = df['before_ip'].values
#         after_ip = df['after_ip'].values
#         n = camera_expected.size
#         before_cat = ["Before"] * n
#         after_cat = ["After"] * n
#
#         # expected = np.concatenate([camera_expected, camera_expected])
#         # values = np.concatenate([before_ip, after_ip])
#         # category = np.concatenate([before_cat, after_cat])
#
#         expected = camera_expected
#         values = after_ip
#         category = after_cat
#
#         df = pd.DataFrame(dict(
#             expected=expected,
#             values=values,
#             category=category
#         ))
#
#         # df = df.loc[(df['expected'] > 40) & (df['expected'] < 45)]
#
#         # embed()
#
#         sns.violinplot(x="expected", y="values", hue="category",
#                        data=df, palette="Set2",# split=True,
#                        scale="count", ax=self.ax)
#
#         # self.ax.set_xscale('log')
#         # self.ax.get_xaxis().set_major_formatter(
#         #     FuncFormatter(lambda x, _: '{:g}'.format(x)))
#         self.ax.set_yscale('log')
#         self.ax.get_yaxis().set_major_formatter(
#             FuncFormatter(lambda x, _: '{:g}'.format(x)))


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

    def plot(self, x, y, yerr=None, label=""):
        (_, caps, _) = self.ax.errorbar(x, y, yerr=yerr,
                                        fmt='o', mew=1,
                                        markersize=3, capsize=3,
                                        elinewidth=0.7, label=label)
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

    output_dir = os.path.join(get_plot("charge_before_after"), subdir)

    output_path = os.path.join(output_dir, "before_mVns_vs_transmission.pdf")
    xlabel = "Transmission"
    ylabel = "Measured Charge (mV ns)"
    p_scatter = ScatterPlotter(xlabel, ylabel)
    for l, file in file_dict.items():
        with ThesisHDF5Reader(file.charge_before_after_path) as r:
            df = r.read('data')
        dead = file.dead
        df = remove_dead_pixels(df, dead)
        df_mean, df_std = get_df_camera_stats(df, "transmission")
        x = df_mean.index
        y = df_mean['before_mVns'].values
        yerr = df_std['before_mVns'].values
        p_scatter.plot(x, y, yerr, l)
    p_scatter.set_log_x()
    p_scatter.set_log_y()
    p_scatter.add_legend('best')
    p_scatter.save(output_path)

    output_path = os.path.join(output_dir, "before_pe_vs_transmission.pdf")
    xlabel = "Transmission"
    ylabel = "Measured Charge (p.e.)"
    p_scatter = ScatterPlotter(xlabel, ylabel)
    for l, file in file_dict.items():
        with ThesisHDF5Reader(file.charge_before_after_path) as r:
            df = r.read('data')
        dead = file.dead
        df = remove_dead_pixels(df, dead)
        df_mean, df_std = get_df_camera_stats(df, "transmission")
        x = df_mean.index
        y = df_mean['before'].values
        yerr = df_std['before'].values
        p_scatter.plot(x, y, yerr, l)
    p_scatter.set_log_x()
    p_scatter.set_log_y()
    p_scatter.add_legend('best')
    p_scatter.save(output_path)

    output_path = os.path.join(output_dir, "after_vs_transmission.pdf")
    xlabel = "Transmission"
    ylabel = "Measured Charge (p.e.)"
    p_scatter = ScatterPlotter(xlabel, ylabel)
    for l, file in file_dict.items():
        with ThesisHDF5Reader(file.charge_before_after_path) as r:
            df = r.read('data')
        dead = file.dead
        df = remove_dead_pixels(df, dead)
        df_mean, df_std = get_df_camera_stats(df, "transmission")
        x = df_mean.index
        y = df_mean['after'].values
        yerr = df_std['after'].values
        p_scatter.plot(x, y, yerr, l)
    p_scatter.set_log_x()
    p_scatter.set_log_y()
    p_scatter.add_legend('best')
    p_scatter.save(output_path)

    output_path = os.path.join(output_dir, "after_ip_vs_transmission.pdf")
    xlabel = "Transmission"
    ylabel = "Measured Charge (p.e.)"
    p_scatter = ScatterPlotter(xlabel, ylabel)
    for l, file in file_dict.items():
        with ThesisHDF5Reader(file.charge_before_after_path) as r:
            df = r.read('data')
        dead = file.dead
        df = remove_dead_pixels(df, dead)
        df_mean, df_std = get_df_camera_stats(df, "transmission")
        x = df_mean.index
        y = df_mean['after_ip'].values
        yerr = df_std['after_ip'].values
        p_scatter.plot(x, y, yerr, l)
    p_scatter.set_log_x()
    p_scatter.set_log_y()
    p_scatter.add_legend('best')
    p_scatter.save(output_path)

    output_path = os.path.join(output_dir, "before_mVns_vs_expected.pdf")
    xlabel = "Charge Expected at Camera Centre (p.e.)"
    ylabel = "Measured Charge (mV ns)"
    p_scatter = ScatterPlotter(xlabel, ylabel)
    for l, file in file_dict.items():
        with ThesisHDF5Reader(file.charge_before_after_path) as r:
            df = r.read('data')
        dead = file.dead
        df = remove_dead_pixels(df, dead)
        df_mean, df_std = get_df_camera_stats(df, "camera_expected")
        x = df_mean.index
        y = df_mean['before_mVns'].values
        yerr = df_std['before_mVns'].values
        p_scatter.plot(x, y, yerr, l)
    p_scatter.set_log_x()
    p_scatter.set_log_y()
    p_scatter.add_legend('best')
    p_scatter.save(output_path)

    output_path = os.path.join(output_dir, "before_pe_vs_expected.pdf")
    xlabel = "Charge Expected at Camera Centre (p.e.)"
    ylabel = "Measured Charge (p.e.)"
    p_scatter = ScatterPlotter(xlabel, ylabel)
    for l, file in file_dict.items():
        with ThesisHDF5Reader(file.charge_before_after_path) as r:
            df = r.read('data')
        dead = file.dead
        df = remove_dead_pixels(df, dead)
        df_mean, df_std = get_df_camera_stats(df, "camera_expected")
        x = df_mean.index
        y = df_mean['before'].values
        yerr = df_std['before'].values
        p_scatter.plot(x, y, yerr, l)
    p_scatter.set_log_x()
    p_scatter.set_log_y()
    p_scatter.add_legend('best')
    p_scatter.save(output_path)

    output_path = os.path.join(output_dir, "after_vs_expected.pdf")
    xlabel = "Charge Expected at Camera Centre (p.e.)"
    ylabel = "Measured Charge (p.e.)"
    p_scatter = ScatterPlotter(xlabel, ylabel)
    for l, file in file_dict.items():
        with ThesisHDF5Reader(file.charge_before_after_path) as r:
            df = r.read('data')
        dead = file.dead
        df = remove_dead_pixels(df, dead)
        df_mean, df_std = get_df_camera_stats(df, "camera_expected")
        x = df_mean.index
        y = df_mean['after'].values
        yerr = df_std['after'].values
        p_scatter.plot(x, y, yerr, l)
    p_scatter.set_log_x()
    p_scatter.set_log_y()
    p_scatter.add_legend('best')
    p_scatter.save(output_path)

    output_path = os.path.join(output_dir, "after_ip_vs_expected.pdf")
    xlabel = "Charge Expected at Camera Centre (p.e.)"
    ylabel = "Measured Charge (p.e.)"
    p_scatter = ScatterPlotter(xlabel, ylabel)
    for l, file in file_dict.items():
        with ThesisHDF5Reader(file.charge_before_after_path) as r:
            df = r.read('data')
        dead = file.dead
        df = remove_dead_pixels(df, dead)
        df_mean, df_std = get_df_camera_stats(df, "camera_expected")
        x = df_mean.index
        y = df_mean['after_ip'].values
        yerr = df_std['after_ip'].values
        p_scatter.plot(x, y, yerr, l)
    p_scatter.set_log_x()
    p_scatter.set_log_y()
    p_scatter.add_legend('best')
    p_scatter.save(output_path)

    output_path = os.path.join(output_dir, "fw_investigation.pdf")
    xlabel = "Transmission"
    ylabel = "Deviation in Effective Transmission"
    p_scatter = ScatterPlotter(xlabel, ylabel)
    for l, file in file_dict.items():
        with ThesisHDF5Reader(file.charge_before_after_path) as r:
            df = r.read('data')
        dead = file.dead
        df = remove_dead_pixels(df, dead)
        df_mean, df_std = get_df_camera_stats(df, "transmission")
        x = df_mean.index
        y = df_mean['before_mVns'].values
        c, m = polyfit(x[22:37], y[22:37], [1])
        y = (y-c)/m / x
        yerr = None
        p_scatter.plot(x, y, yerr, l)
    p_scatter.set_log_x()
    p_scatter.add_legend('best')
    p_scatter.save(output_path)

    output_path = os.path.join(output_dir, "fw_investigation_fwpos.pdf")
    xlabel = "FW_POS"
    ylabel = "Deviation in Effective FW_POS"
    p_scatter = ScatterPlotter(xlabel, ylabel)
    for l, file in file_dict.items():
        with ThesisHDF5Reader(file.charge_before_after_path) as r:
            df = r.read('data')
        dead = file.dead
        df = remove_dead_pixels(df, dead)
        df_mean, df_std = get_df_camera_stats(df, "fw_pos")
        x = df_mean.index
        y = df_mean['before_mVns'].values
        yerr = None
        p_scatter.plot(x, y, yerr, l)
    p_scatter.set_log_y()
    p_scatter.add_legend('best')
    p_scatter.save(output_path)


def main():
    file_dict = {
        "200ADC-GM": Lab_GM200ADC(),
        "100ADC-GM": Lab_GM100ADC(),
        "50ADC-GM": Lab_GM50ADC(),
    }
    subdir = "vb_comparison"
    process(file_dict, subdir)

    # file_dict = {
    #     "CHEC-M": CHECM(),
    # }
    # subdir = "checm"
    # process(file_dict, subdir)


if __name__ == '__main__':
    main()

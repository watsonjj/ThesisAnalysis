from ThesisAnalysis.plotting.setup import ThesisPlotter
from ThesisAnalysis import get_data, get_plot, ThesisHDF5Reader
from ThesisAnalysis.plotting.camera import CameraImage
import numpy as np
from CHECLabPy.waveform_reducers.cross_correlation import CrossCorrelation
from matplotlib.cm import get_cmap
from matplotlib.ticker import FuncFormatter


class GMPlotter(ThesisPlotter):
    def plot(self, before, after, gamma_q):

        std = np.std(before)
        std_pe = std / gamma_q
        l = ("Before Gain Matching\n"
             r"$(\sigma = \SI{{{:#.3g}}}{{mV}} = \SI{{{:#.3g}}}{{\pe}})").format(std, std_pe)
        self.ax.hist(before, bins=100, label=l, alpha=0.9)

        std = np.std(after)
        std_pe = std / gamma_q
        l = ("After Gain Matching\n"
             r"$(\sigma = \SI{{{:#.3g}}}{{mV}} = \SI{{{:#.3g}}}{{\pe}})").format(std, std_pe)
        self.ax.hist(after, bins=100, label=l, alpha=0.9)

        self.ax.set_xlabel("Waveform Amplitude (mV)")
        self.ax.set_ylabel("Number of Pixels")
        self.add_legend(1)


class FFPlotter(ThesisPlotter):
    def plot(self, before, after, after_ip, exp, experr):

        mean = np.mean(before)
        std = np.std(before)
        l = ("Before Flat Field \n"
             r"$(\mu = \SI{{{:#.3g}}}{{\pe}}, \sigma = \SI{{{:#.3g}}}{{\pe}}$)").format(mean, std)
        self.ax.hist(before, bins=100, label=l, alpha=0.9)

        mean = np.mean(after)
        std = np.std(after)
        l = ("After Flat Field \n"
             r"$(\mu = \SI{{{:#.3g}}}{{\pe}}, \sigma = \SI{{{:#.3g}}}{{\pe}}$)").format(mean, std)
        self.ax.hist(after, bins=30, label=l, alpha=0.9)

        mean = np.mean(after_ip)
        std = np.std(after_ip)
        l = ("After Flat Field, Corrected for Illumination Profile\n"
             r"$(\mu = \SI{{{:#.3g}}}{{\pe}}, \sigma = \SI{{{:#.3g}}}{{\pe}}$)").format(mean, std)
        if self.sidebyside:
            l = ("After Flat Field, Corrected\n"
                 r"$(\mu = \SI{{{:#.3g}}}{{\pe}}, \sigma = \SI{{{:#.3g}}}{{\pe}}$)").format(mean, std)
        self.ax.hist(after_ip, bins="auto", label=l, alpha=0.9, color='black')

        t = r"$Q_\text{{Exp}} = \SI[separate-uncertainty = true]{{{:#.2f} \pm {:#.2f}}}{{\pe}}$"
        self.ax.text(0.05, 0.2, t.format(exp, experr), transform=self.ax.transAxes)

        self.ax.set_xlabel("Waveform Charge (p.e.)")
        self.ax.set_ylabel("Number of Pixels")
        self.add_legend(2)


class StdPlotter(ThesisPlotter):
    def plot(self, df):
        df_mean = df.groupby("expected").transform(np.mean)
        df['before_norm'] = df['before'] / df_mean['before']
        df['after_norm'] = df['after'] / df_mean['after']
        df['after_ip_norm'] = df['after_ip'] / df_mean['after_ip']
        df_std = df.groupby('expected').std()

        x = df_std.index.values
        y = df_std['before_norm'] * 100
        l = "Before"
        self.ax.plot(x, y, 'o-', ms=2, label=l)

        x = df_std.index.values
        y = df_std['after_norm'] * 100
        l = "After"
        self.ax.plot(x, y, 'o-', ms=2, label=l)

        x = df_std.index.values
        y = df_std['after_ip_norm'] * 100
        l = "After, Corrected for Illumination Profile"
        self.ax.plot(x, y, 'o-', color='black', ms=2, label=l)

        self.ax.set_xscale('log')
        self.ax.get_xaxis().set_major_formatter(
            FuncFormatter(lambda xl, _: '{:g}'.format(xl)))

        self.ax.set_xlabel("Average Expected Charge (p.e.)")
        self.ax.set_ylabel("Average Charge Spread Between Pixels (%)")
        self.add_legend("best")


def process_gm(input_path, output_path, ff_path):
    with ThesisHDF5Reader(input_path) as reader:
        df = reader.read("data")
        before = df['before'].values
        after = df['after'].values
        metadata = reader.read_metadata()
        n_pixels = metadata['n_pixels']
        n_samples = metadata['n_samples']
        reference_pulse_path = metadata['reference_pulse_path']

    with ThesisHDF5Reader(ff_path) as reader:
        df = reader.read("data")
        gamma_q = df['gamma_q'].values[0]
        gamma_q_err = df['gamma_q_err'].values[0]
        gamma_ff = df['gamma_ff'].values

    cc = CrossCorrelation(n_pixels, n_samples,
                          reference_pulse_path=reference_pulse_path)
    gamma_q_mV = cc.get_pulse_height(gamma_q)
    gamma_q_err_mV = cc.get_pulse_height(gamma_q_err)

    print(r"$\gamma_Q_mV$ = {:.3f} ± {:.3f}".format(gamma_q_mV, gamma_q_err_mV))

    p_hist = GMPlotter()
    p_hist.plot(before, after, gamma_q_mV)
    p_hist.save(output_path)


def process_ff(input_path, output_path, sidebyside=False):
    with ThesisHDF5Reader(input_path) as reader:
        df = reader.read("data")
        before = df['before'].values
        after = df['after'].values
        after_ip = df['after_ip'].values
        metadata = reader.read_metadata()
        exp = metadata['expected']
        experr = metadata['expected_err']

    p_hist = FFPlotter(sidebyside=sidebyside)
    p_hist.plot(before, after, after_ip, exp, experr)
    p_hist.save(output_path)


def process_ff_values(input_path, output_path, dead):
    with ThesisHDF5Reader(input_path) as reader:
        df = reader.read("data")
        gamma_q = df['gamma_q'].values[0]
        gamma_q_err = df['gamma_q_err'].values[0]
        gamma_ff = df['gamma_ff'].values
        mapping = reader.read_mapping()

    mask = np.zeros(gamma_ff.shape, dtype=np.bool)
    mask[dead] = 1

    print(r"$\gamma_Q$ = {:.3f} ± {:.3f}".format(gamma_q, gamma_q_err))

    cmap = get_cmap('viridis')
    cmap.set_under('black')
    cmap.set_over('white')

    p_image = CameraImage.from_mapping(mapping, cmap=cmap)
    p_image.image = gamma_ff
    p_image.highlight_pixels(dead, color='red')
    p_image.add_colorbar(label=r"${{\gamma_{{FF}}}}_i$", extend='both')
    p_image.set_limits_minmax(gamma_ff[~mask].min(), gamma_ff[~mask].max())
    p_image.colorbar.ax.minorticks_off()
    p_image.save(output_path)


def process_ff_all(input_path, output_path):
    with ThesisHDF5Reader(input_path) as reader:
        df = reader.read("data")

    p = StdPlotter()
    p.plot(df)
    p.save(output_path)


def main():
    input_path = get_data("before_after_gm.h5")
    output_path = get_plot("before_after_gm_ff/before_after_gm.pdf")
    ff_path = get_data("ff_values.h5")
    process_gm(input_path, output_path, ff_path)

    input_path = get_data("before_after_ff_50pe.h5")
    output_path = get_plot("before_after_gm_ff/before_after_ff_50pe.pdf")
    process_ff(input_path, output_path)

    input_path = get_data("before_after_ff_25pe.h5")
    output_path = get_plot("before_after_gm_ff/before_after_ff_25pe.pdf")
    process_ff(input_path, output_path, True)

    input_path = get_data("before_after_ff_100pe.h5")
    output_path = get_plot("before_after_gm_ff/before_after_ff_100pe.pdf")
    process_ff(input_path, output_path, True)

    input_path = get_data("ff_values.h5")
    output_path = get_plot("before_after_gm_ff/ff_values.pdf")
    dead = [677, 293, 27, 1925]
    process_ff_values(input_path, output_path, dead)

    input_path = get_data("before_after_ff_all.h5")
    output_path = get_plot("before_after_gm_ff/before_after_ff_all.pdf")
    process_ff_all(input_path, output_path)


if __name__ == '__main__':
    main()

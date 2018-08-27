from matplotlib.ticker import FuncFormatter

from ThesisAnalysis.plotting.setup import ThesisPlotter
from ThesisAnalysis import get_data, get_plot, ThesisHDF5Writer, \
    ThesisHDF5Reader
from ThesisAnalysis.plotting.camera import CameraImage
import numpy as np
import pandas as pd
from CHECLabPy.waveform_reducers.cross_correlation import CrossCorrelation
from matplotlib.cm import get_cmap


class GMPlotter(ThesisPlotter):
    def plot(self, before, after, gamma_q):

        std = np.std(before)
        std_pe = std / gamma_q
        l = "Before (StdDev = {:.3g} mV = {:.3g} p.e.)".format(std, std_pe)
        self.ax.hist(before, bins=100, label=l, alpha=0.9)

        std = np.std(after)
        std_pe = std / gamma_q
        l = "After (StdDev = {:.3g} mV = {:.3g} p.e.)".format(std, std_pe)
        self.ax.hist(after, bins=100, label=l, alpha=0.9)

        self.ax.set_xlabel("Waveform Amplitude (mV)")
        self.ax.set_ylabel("Number of Pixels")
        self.add_legend(1)


class FFPlotter(ThesisPlotter):
    def plot(self, before, after, after_ip):

        mean = np.mean(before)
        std = np.std(before)
        l = "Before (Mean = {:.3g}, StdDev = {:.3g} p.e.)".format(mean, std)
        self.ax.hist(before, bins=100, label=l, alpha=0.9)

        mean = np.mean(after)
        std = np.std(after)
        l = "After (Mean = {:.3g}, StdDev = {:.3g} p.e.)".format(mean, std)
        self.ax.hist(after, bins=30, label=l, alpha=0.9)

        mean = np.mean(after_ip)
        std = np.std(after_ip)
        l = "After, Corrected for Illumination Profile\n(Mean = {:.3g}, StdDev = {:.3g} p.e.)".format(mean, std)
        self.ax.hist(after_ip, bins=30, label=l, alpha=0.9, color='black')

        self.ax.set_xlabel("Waveform Charge (p.e.)")
        self.ax.set_ylabel("Number of Pixels")
        self.add_legend(2)


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
        gamma_ff = df['gamma_ff'].values

    cc = CrossCorrelation(n_pixels, n_samples,
                          reference_pulse_path=reference_pulse_path)
    gamma_q_mV = cc.get_pulse_height(gamma_q)

    p_hist = GMPlotter()
    p_hist.plot(before, after, gamma_q_mV)
    p_hist.save(output_path)


def process_ff(input_path, output_path):
    with ThesisHDF5Reader(input_path) as reader:
        df = reader.read("data")
        before = df['before'].values
        after = df['after'].values
        after_ip = df['after_ip'].values

    p_hist = FFPlotter()
    p_hist.plot(before, after, after_ip)
    p_hist.save(output_path)


def process_ff_values(input_path, output_path, dead):
    with ThesisHDF5Reader(input_path) as reader:
        df = reader.read("data")
        gamma_q = df['gamma_q'].values[0]
        gamma_ff = df['gamma_ff'].values
        mapping = reader.read_mapping()

    mask = np.zeros(gamma_ff.shape, dtype=np.bool)
    mask[dead] = 1

    print("Gamma_Q = {:.3f}".format(gamma_q))

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


def main():
    input_path = get_data("before_after_gm.h5")
    output_path = get_plot("before_after_gm_ff/before_after_gm.pdf")
    ff_path = get_data("ff_values.h5")
    process_gm(input_path, output_path, ff_path)

    input_path = get_data("before_after_ff.h5")
    output_path = get_plot("before_after_gm_ff/before_after_ff.pdf")
    process_ff(input_path, output_path)

    input_path = get_data("ff_values.h5")
    output_path = get_plot("before_after_gm_ff/ff_values.pdf")
    dead = [677, 293, 27, 1925]
    process_ff_values(input_path, output_path, dead)


if __name__ == '__main__':
    main()

from ThesisAnalysis.plotting.setup import ThesisPlotter
from ThesisAnalysis import get_data, get_plot, ThesisHDF5Reader
import numpy as np
import os
from tqdm import tqdm
from scipy import interpolate
from scipy.ndimage import correlate1d
from matplotlib import pyplot as plt, animation
from matplotlib.ticker import MultipleLocator
from CHECLabPy.plotting.setup import Plotter
from CHECLabPy.plotting.waveform import WaveformPlotter
from CHECLabPy.waveform_reducers.cross_correlation import CrossCorrelation as CC
from target_calib import CameraConfiguration
from IPython import embed


class CrossCorrelation:
    def __init__(self, n_samples):
        ref_path = CameraConfiguration("1.1.0").GetReferencePulsePath()
        cc = CC(1, 1, reference_pulse_path=ref_path)
        self.reference_pulse = cc.reference_pulse
        self.n_samples = n_samples
        self.ref_pad = np.pad(self.reference_pulse, n_samples, 'constant')
        self.ref_t_start = self.ref_pad.size // 2
        self.ref_t_end = self.ref_t_start + n_samples

    def ref_t(self, t):
        if t > self.n_samples:
            raise IndexError
        start = self.ref_t_start - t
        end = self.ref_t_end - t
        return self.ref_pad[start:end]

    def multiply(self, waveform, t):
        return waveform * self.ref_t(t)

    def cc_point(self, waveform, t):
        return np.sum(self.multiply(waveform, t))

    def cc(self, waveform):
        result = np.zeros(self.n_samples)
        for t in range(self.n_samples):
            result[t] = self.cc_point(waveform, t)
        return result


class CCPlot(ThesisPlotter):
    def __init__(self):
        super().__init__(sidebyside=True)

        figsize = self.get_figsize()
        figsize[1] *= 3
        self.fig = plt.figure(figsize=figsize)
        self.ax1 = self.fig.add_subplot(3, 1, 1)
        self.ax1t = self.ax1.twinx()
        self.ax2 = self.fig.add_subplot(3, 1, 2)
        self.ax3 = self.fig.add_subplot(3, 1, 3)

        self.n_samples = None
        self.source = None

        self.c1 = next(self.ax._get_lines.prop_cycler)['color']
        self.c2 = next(self.ax._get_lines.prop_cycler)['color']

    @staticmethod
    def align_yaxis(ax1, ax2):
        """Align zeros of the two axes, zooming them out by same ratio"""
        axes = np.array([ax1, ax2])
        extrema = np.array([ax.get_ylim() for ax in axes])
        tops = extrema[:, 1] / (extrema[:, 1] - extrema[:, 0])
        # Ensure that plots (intervals) are ordered bottom to top:
        if tops[0] > tops[1]:
            axes, extrema, tops = [a[::-1] for a in (axes, extrema, tops)]

        # How much would the plot overflow if we kept current zoom levels?
        tot_span = tops[1] + 1 - tops[0]

        extrema[0, 1] = extrema[0, 0] + tot_span * (
                    extrema[0, 1] - extrema[0, 0])
        extrema[1, 0] = extrema[1, 1] + tot_span * (
                    extrema[1, 0] - extrema[1, 1])
        [axes[i].set_ylim(*extrema[i]) for i in range(2)]

    def plot(self, wf, python_cc, t0):
        self.n_samples = wf.size

        cc_result = python_cc.cc(wf)
        if t0 is None:
            t = np.argmax(cc_result)
        else:
            t = t0
        ref = python_cc.ref_t(t)
        multiply = python_cc.multiply(wf, t)

        self.ax1.plot(wf, color=self.c1, label="Waveform")
        self.ax1t.plot(ref, color=self.c2, label="Reference")
        self.ax2.plot(multiply, color=self.c1)
        self.ax3.plot(cc_result, color=self.c1)

        l_tline = self.ax3.axvline(t, ls='--', c='black')

        self.align_yaxis(self.ax1, self.ax1t)

    def finish(self):
        self.ax1.set_title("Waveforms")
        self.ax2.set_title("Multiply")
        self.ax3.set_title("Cross-correlation")
        self.ax1.set_ylabel("Waveform Amplitude (mV)")
        self.ax1t.set_ylabel("Reference Amplitude")
        self.ax2.set_ylabel("Amplitude (mV)")
        self.ax3.set_ylabel("Amplitude (mV ns)")
        self.ax3.set_xlabel("Time (ns)")
        self.ax1.xaxis.set_major_locator(MultipleLocator(16))
        self.ax2.xaxis.set_major_locator(MultipleLocator(16))
        self.ax3.xaxis.set_major_locator(MultipleLocator(16))
        self.ax1.tick_params(axis='y', labelcolor=self.c1)
        self.ax1t.tick_params(axis='y', labelcolor=self.c2)

        self.ax1.yaxis.set_label_coords(-0.15, 0.5)
        self.ax2.yaxis.set_label_coords(-0.15, 0.5)
        self.ax3.yaxis.set_label_coords(-0.15, 0.5)

        self.ax1t.relim()
        self.ax1t.autoscale_view()

        self.fig.tight_layout()


def process(input_path, output_path, t0):
    with ThesisHDF5Reader(input_path) as reader:
        df = reader.read('data')
        wf = df['wf'].values

    n_samples = wf.size

    python_cc = CrossCorrelation(n_samples)

    p_result = CCPlot()
    p_result.plot(wf, python_cc, t0)
    p_result.save(output_path)


def main():
    input_path = get_data("annotated_waveform/checs_3pe.h5")
    output_path = get_plot("cross_correlation/cc_tmax.pdf")
    t0 = None
    process(input_path, output_path, t0)

    input_path = get_data("annotated_waveform/checs_3pe.h5")
    output_path = get_plot("cross_correlation/cc_tnsb.pdf")
    t0 = 19
    process(input_path, output_path, t0)


    input_path = get_data("annotated_waveform/checs_3pe.h5")
    output_path = get_plot("cross_correlation/cc_tnoise.pdf")
    t0 = 106
    process(input_path, output_path, t0)



if __name__ == '__main__':
    main()
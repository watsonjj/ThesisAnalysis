from ThesisAnalysis import get_data, get_plot, ThesisHDF5Reader
from ThesisAnalysis.plotting.setup import ThesisPlotter
import numpy as np
from matplotlib.ticker import MultipleLocator
from matplotlib.colors import LogNorm
from IPython import embed


class Waveform(ThesisPlotter):
    def plot(self, wf, fit):
        self.ax.plot(wf, color='black', label="TARGET-C Waveform")
        self.ax.plot(fit, color='red', ls=':', label="Landau Fit")
        self.ax.plot(np.zeros(wf.size), color='gray', label="")

        tmin = fit.argmin()
        tmax = fit.argmax()
        amin = wf[tmin]
        amax = wf[tmax]
        self.ax.arrow(tmin, 0, 0, amin, ls='-', color='red', head_width=2,
                      head_length=40, length_includes_head=True)
        self.ax.arrow(tmax, 0, 0, amax, ls='-', color='red', head_width=2,
                      head_length=40, length_includes_head=True)

        self.ax.set_xlabel("Time (ns)")
        self.ax.set_ylabel("Amplitude (mV)")

        self.add_legend('best')

        self.ax.xaxis.set_major_locator(MultipleLocator(16))


def process(input_path, output_path):
    x, wf, fit = np.loadtxt(input_path, unpack=True)

    p_wf = Waveform()
    p_wf.plot(wf, fit)
    p_wf.save(output_path)


def main():
    input_path = get_data("pulse_fit.txt")
    output_path = get_plot("tf/tf_pulse_fit.pdf")
    process(input_path, output_path)


if __name__ == '__main__':
    main()

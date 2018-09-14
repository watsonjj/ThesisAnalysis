from ThesisAnalysis import get_data, get_plot, ThesisHDF5Reader
from ThesisAnalysis.plotting.setup import ThesisPlotter
import numpy as np
from matplotlib.ticker import MultipleLocator
from matplotlib.colors import LogNorm
from IPython import embed


class Waveform(ThesisPlotter):
    def plot(self, wf):
        self.ax.plot(wf, color='black')

        color = next(self.ax._get_lines.prop_cycler)['color']
        s = np.s_[48:100]
        x = np.arange(wf.size)[s]
        y1 = wf[s]
        y2 = np.zeros(wf.size)[s]
        self.ax.fill_between(x, y1, y2, lw=0, color=color, alpha=0.5)
        self.ax.text(71, 3, "Signal Pulse", color=color)

        color = next(self.ax._get_lines.prop_cycler)['color']
        s = np.s_[11:54]
        x = np.arange(wf.size)[s]
        y1 = wf[s]
        y2 = np.zeros(wf.size)[s]
        self.ax.fill_between(x, y1, y2, lw=0, color=color, alpha=0.5)
        self.ax.text(5, 4.2, "NSB/Dark-Count Pulse", color=color)

        s = np.s_[115:]
        x = np.arange(wf.size)[s]
        y1 = wf[s]
        y2 = np.zeros(wf.size)[s]
        self.ax.fill_between(x, y1, y2, lw=0, color=color, alpha=0.5)

        local_max = np.argmax(wf)
        self.ax.axvline(local_max, ls=':', color='black')
        self.ax.text(local_max, -2, "Local Peak Time", color='black', rotation=90, ha='right', va='bottom')

        global_max = 62
        self.ax.axvline(global_max, ls='--', color='black')
        self.ax.text(global_max+1, -2, "Global Peak Time", color='black', rotation=90, va='bottom')

        color = next(self.ax._get_lines.prop_cycler)['color']
        s = np.s_[100:115]
        x = np.arange(wf.size)
        self.ax.plot(x[s], wf[s], color=color)
        self.ax.text(90, -2, "Electronic Noise", color=color)

        self.ax.set_xlabel("Time (ns)")
        self.ax.set_ylabel("Amplitude (mV)")

        self.ax.xaxis.set_major_locator(MultipleLocator(16))


def process(input_path, output_path):
    with ThesisHDF5Reader(input_path) as reader:
        df = reader.read('data')
        wf = df['wf'].values

    p_wf = Waveform()
    p_wf.plot(wf)
    p_wf.save(output_path)


def main():
    input_path = get_data("annotated_waveform/checs_3pe.h5")
    output_path = get_plot("annotated_waveform/checs_3pe.pdf")
    process(input_path, output_path)


if __name__ == '__main__':
    main()
from ThesisAnalysis import get_data, get_plot, ThesisHDF5Reader
from ThesisAnalysis.plotting.setup import ThesisPlotter
import numpy as np
from matplotlib.ticker import MultipleLocator
from matplotlib.colors import LogNorm
from IPython import embed


class Image(ThesisPlotter):
    def plot(self, x, y, z):

        xp = x[np.nanargmax(z)]
        yp = y[np.nanargmax(z)]
        zp_max = np.nanmax(z)
        zp_min = np.nanmin(z)
        self.ax.plot(xp, yp, 'x', color='red', ms=4)
        self.ax.text(xp+0.5, yp+1, '({}, {})'.format(xp, yp), color='red')
        # levels = np.linspace(0, zp_max, 21)
        levels = np.linspace(zp_min, zp_max, 21)


        nx = np.arange(np.min(x), np.max(x) + 2) - 0.5
        ny = np.arange(np.min(y), np.max(y) + 2) - 0.5
        # counts, xbins, ybins = np.histogram2d(x, y, weights=z, bins=(nx, ny))
        counts, xbins, ybins, image = self.ax.hist2d(x, y, weights=z, bins=(nx, ny))
        image = self.ax.contourf(counts.T, extent=[xbins[0], xbins[-1], ybins[0], ybins[-1]], levels=levels)



        self.fig.colorbar(image, label="Signal-to-Noise")

        # self.ax.minorticks_off()
        # self.ax.xaxis.set_major_locator(MultipleLocator(2))
        # self.ax.yaxis.set_major_locator(MultipleLocator(2))
        self.ax.set_xlabel('Integration-Window Size')
        self.ax.set_ylabel('Integration-Window Shift')


class Waveform(ThesisPlotter):
    def plot(self, wf):
        self.ax.plot(wf, color='black')

        s = np.s_[48:100]
        x = np.arange(wf.size)[s]
        y1 = wf[s]
        y2 = np.zeros(wf.size)[s]
        self.ax.fill_between(x, y1, y2, lw=0, color='blue', alpha=0.5)
        self.ax.text(71, 3, "Signal Pulse", color='blue')
        self.ax.text(76, -2, "(Signal Undershoot)", color='blue')

        s = np.s_[11:54]
        x = np.arange(wf.size)[s]
        y1 = wf[s]
        y2 = np.zeros(wf.size)[s]
        self.ax.fill_between(x, y1, y2, lw=0, color='red', alpha=0.5)
        self.ax.text(5, 4.2, "NSB/Dark-Count Pulse", color='red')

        s = np.s_[115:]
        x = np.arange(wf.size)[s]
        y1 = wf[s]
        y2 = np.zeros(wf.size)[s]
        self.ax.fill_between(x, y1, y2, lw=0, color='red', alpha=0.5)

        local_max = np.argmax(wf)
        self.ax.axvline(local_max, ls=':', color='black')
        self.ax.text(local_max, -2, "Local Peak Time", color='black', rotation=90, ha='right', va='bottom')

        global_max = 62
        self.ax.axvline(global_max, ls='--', color='black')
        self.ax.text(global_max+1, -2, "Global Peak Time", color='black', rotation=90, va='bottom')

        # size = 5
        # shift = 2
        #
        # t_max = wf.argmax()
        # start = t_max - shift
        # end = start + size - 1
        # self.ax.axvspan(start, end, hatch='/', color='blue', fill=False)
        # self.ax.text(end + 1, 6, "ON", color='blue')
        #
        # self.ax.axvline(t_max, linestyle='--', color='gray')
        # self.ax.arrow(t_max, 0.4, -shift, 0, color='gray', head_width=0.1,
        #               head_length=0.5, length_includes_head=True)
        # self.ax.text(start, 0.4, "Shift = 2", color='gray', ha='right', va='bottom', rotation=90)
        # self.ax.arrow(start, 0.2, size-1, 0, color='gray', head_width=0.1,
        #               head_length=0.5, length_includes_head=True)
        # self.ax.text(end+0.5, 0.2, "Size = 5", color='gray', ha='left', va='bottom', rotation=90)
        #
        # start = 0
        # end = start + size - 1
        # self.ax.axvspan(start, end, hatch='/', color='red', fill=False)
        # self.ax.text(end + 1, 6, "OFF", color='red')
        # self.ax.arrow(start, 0.2, size-1, 0, color='gray', head_width=0.1,
        #               head_length=0.5, length_includes_head=True)
        # self.ax.text(end+0.5, 0.2, "Size = 5", color='gray', ha='left', va='bottom', rotation=90)

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
from ThesisAnalysis.plotting.setup import ThesisPlotter
from ThesisAnalysis import get_data, get_plot, ThesisHDF5Reader
import os
import numpy as np
from matplotlib.ticker import MultipleLocator
from target_calib import CalculateRowColumnBlockPhase, GetCellIDTCArray


class Waveform(ThesisPlotter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.axr1 = self.ax
        self.axr0 = self.ax.twinx()

    @staticmethod
    def align_yaxis(ax1, v1, ax2, v2):
        """adjust ax2 ylimit so that v2 in ax2 is aligned to v1 in ax1"""
        _, y1 = ax1.transData.transform((0, v1))
        _, y2 = ax2.transData.transform((0, v2))
        Waveform.adjust_yaxis(ax2, (y1 - y2) / 2, v2)
        Waveform.adjust_yaxis(ax1, (y2 - y1) / 2, v1)

    @staticmethod
    def adjust_yaxis(ax, ydif, v):
        """shift axis ax by ydiff, maintaining point v at the same location"""
        inv = ax.transData.inverted()
        _, dy = inv.transform((0, 0)) - inv.transform((0, ydif))
        miny, maxy = ax.get_ylim()
        miny, maxy = miny - v, maxy - v
        if -miny > maxy or (-miny == maxy and dy > 0):
            nminy = miny
            nmaxy = miny * (maxy + dy) / (miny + dy)
        else:
            nmaxy = maxy
            nminy = maxy * (miny + dy) / (maxy + dy)
        ax.set_ylim(nminy + v, nmaxy + v)

    def plot(self, df, event):
        df_event = df.loc[df['iev'] == event]
        x = df_event['isam']
        yr1 = df_event['r1']
        yr0 = df_event['r0']

        cr1 = next(self.ax._get_lines.prop_cycler)['color']
        cr0 = next(self.ax._get_lines.prop_cycler)['color']

        self.axr1.plot(x, yr1, color=cr1)
        self.axr0.plot(x, yr0, color=cr0)

        self.axr1.set_xlabel("Time (ns)")
        self.axr1.set_ylabel("Amplitude (Pedestal-Subtracted ADC)", color=cr1)
        self.axr0.set_ylabel("Amplitude (Raw ADC)", color=cr0)
        self.axr1.tick_params('y', which='both', colors=cr1)
        self.axr0.tick_params('y', which='both', colors=cr0)

        self.axr1.xaxis.set_major_locator(MultipleLocator(16))
        self.axr0.xaxis.set_major_locator(MultipleLocator(16))

        self.align_yaxis(self.axr1, yr1.mean(), self.axr0, yr0.mean())


def main():
    path = get_data("pedestal_pulse_checs.h5")
    with ThesisHDF5Reader(path) as reader:
        df = reader.read("data")

    eoi = 10
    p_wf = Waveform(sidebyside=True)
    p_wf.plot(df, eoi)
    p_wf.save(get_plot("pulse_raw_vs_pedestal.pdf"))


if __name__ == '__main__':
    main()

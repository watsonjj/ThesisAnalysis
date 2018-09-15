from ThesisAnalysis.plotting.setup import ThesisPlotter
from ThesisAnalysis.plotting.camera import CameraImage
from ThesisAnalysis import get_data, get_plot, ThesisHDF5Reader
from ThesisAnalysis.files import Lab_Window
from CHECLabPy.core.io import DL1Reader
import numpy as np
import pandas as pd
import os


class Hist(ThesisPlotter):
    def plot(self, values, dead_mask):
        values = values[~dead_mask]

        self.ax.hist(values, bins='auto')

        self.ax.set_xlabel("Time Correction (ns)")
        self.ax.set_ylabel("N (Pixels)")


def process(input_path, output_dir):

    with ThesisHDF5Reader(input_path) as reader:
        t_corr = reader.read("data")['t_corr'].values
        metadata = reader.read_metadata()
        dead = metadata['dead']
        n_pixels = metadata['n_pixels']
        mapping = reader.read_mapping()

    dead_mask = np.zeros(n_pixels, dtype=np.bool)
    dead_mask[dead] = True

    p_hist = Hist()
    p_hist.plot(t_corr, dead_mask)
    output_path = os.path.join(output_dir, "hist.pdf")
    p_hist.save(output_path)

    p_image = CameraImage.from_mapping(mapping)
    p_image.image = t_corr
    p_image.highlight_pixels(dead, color='red')
    p_image.add_colorbar(label="Time Correction (ns)")
    p_image.colorbar.ax.minorticks_off()
    output_path = os.path.join(output_dir, "image.pdf")
    p_image.save(output_path)


def main():
    input_path = get_data("time_corrections/time_corrections_lab.h5")
    output_dir = get_plot("time_corrections/lab")
    process(input_path, output_dir)

    input_path = get_data("time_corrections/time_corrections_mc.h5")
    output_dir = get_plot("time_corrections/mc")
    process(input_path, output_dir)

    input_path = get_data("time_corrections/time_corrections_checm.h5")
    output_dir = get_plot("time_corrections/checm")
    process(input_path, output_dir)


if __name__ == '__main__':
    main()
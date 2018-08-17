from ThesisAnalysis.plotting.resolutions import ChargeResolutionPlotter, \
    ChargeResolutionWRRPlotter, ChargeMeanPlotter
from ThesisAnalysis import get_plot
import os
import numpy as np


class PlotHandler:
    def __init__(self):
        self.p_cr = ChargeResolutionPlotter()
        self.p_crwrr = ChargeResolutionWRRPlotter()
        self.p_mean = ChargeMeanPlotter()

    def plot_pixel(self, path, label, poi):
        self.p_cr.set_path(path)
        self.p_cr.plot_pixel(poi, label + " (pixel {})".format(poi))
        self.p_crwrr.set_path(path)
        self.p_crwrr.plot_pixel(poi, label + " (pixel {})".format(poi))
        self.p_mean.set_path(path)
        self.p_mean.plot_pixel(poi, label + " (pixel {})".format(poi))

    def plot_camera(self, path, label):
        self.p_cr.set_path(path)
        self.p_cr.plot_camera(label)
        self.p_crwrr.set_path(path)
        self.p_crwrr.plot_camera(label)
        self.p_mean.set_path(path)
        self.p_mean.plot_camera(label)

    def plot_pixel_from_dict(self, path_dict, poi):
        for label, path in path_dict.items():
            self.plot_pixel(path, label, poi)

    def plot_camera_from_dict(self, path_dict):
        for label, path in path_dict.items():
            self.plot_camera(path, label)

    def save(self, output_dir):
        true = np.geomspace(0.1, 2000, 1000)
        self.p_cr.plot_requirement(true)
        self.p_cr.plot_poisson(true)
        self.p_cr.add_legend("best")
        self.p_crwrr.plot_requirement(true)
        self.p_crwrr.plot_poisson(true)
        self.p_crwrr.add_legend("best")
        self.p_mean.add_legend("best")

        self.p_cr.save(os.path.join(output_dir, "charge_res.pdf"))
        self.p_crwrr.save(os.path.join(output_dir, "charge_res_wrr.pdf"))
        self.p_mean.save(os.path.join(output_dir, "charge_mean.pdf"))


def main():
    # poi = 888
    # poi = 1344
    # poi = 969
    poi = 15

    mclab_0mhz = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/0mhz/charge_resolution.h5"
    mclab_5mhz = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/5mhz/charge_resolution.h5"
    mclab_40mhz = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/40mhz/charge_resolution.h5"
    mclab_125mhz = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/125mhz/charge_resolution.h5"
    mclab_1200mhz = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/1200mhz/charge_resolution.h5"
    lab_tfnone = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_none/charge_resolution.h5"
    lab_tfpchip = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_pchip/charge_resolution.h5"
    lab_tfpoly = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_poly/charge_resolution.h5"
    lab_tfwithped = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_withped/charge_resolution.h5"
    mclab_0mhz_0mhzfw = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/0mhz/charge_resolution_0mhzfw.h5"

    output_dir = get_plot("charge_resolution/lab_vs_mc")
    path_dict = {
        "MC-Lab 0MHz": mclab_0mhz,
        "MC-Lab 5MHz": mclab_5mhz,
        "MC-Lab 40MHz": mclab_40mhz,
        "MC-Lab 125MHz": mclab_125mhz,
        "MC-Lab 1200MHz": mclab_1200mhz,
        "Lab (TF-Poly)": lab_tfpoly,
    }
    ph = PlotHandler()
    ph.plot_pixel_from_dict(path_dict, poi)
    ph.save(output_dir)

    output_dir = get_plot("charge_resolution/tf_comparison")
    path_dict = {
        "Lab (No TF)": lab_tfnone,
        "Lab (TF-PCHIP)": lab_tfpchip,
        "Lab (TF-Poly)": lab_tfpoly,
        "Lab (TF-WithPedestal)": lab_tfwithped,
    }
    ph = PlotHandler()
    ph.plot_pixel_from_dict(path_dict, poi)
    # ph.plot_camera_from_dict(path_dict)
    ph.save(output_dir)

    # output_dir = get_plot("charge_resolution/0mhz_or_5mhz_fw")
    # path_dict = {
    #     "MC-Lab 0MHz (5MHz FW Calibration)": mclab_0mhz,
    #     "MC-Lab 0MHz (0MHz FW Calibration)": mclab_0mhz_0mhzfw,
    # }
    # ph = PlotHandler()
    # ph.plot_pixel_from_dict(path_dict, poi)
    # ph.save(output_dir)


if __name__ == '__main__':
    main()

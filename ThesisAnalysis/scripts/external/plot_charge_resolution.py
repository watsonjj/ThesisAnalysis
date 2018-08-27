from ThesisAnalysis.plotting.resolutions import ChargeResolutionPlotter, \
    ChargeResolutionWRRPlotter, ChargeMeanPlotter
from ThesisAnalysis.files import *
from ThesisAnalysis import get_plot
import os
import numpy as np


class PlotHandler:
    def __init__(self):
        self.p_cr = ChargeResolutionPlotter()
        self.p_crwrr = ChargeResolutionWRRPlotter()
        self.p_mean = ChargeMeanPlotter()

    def plot_pixel(self, file, label, poi):
        path = file.charge_resolution_path

        self.p_cr.set_path(path)
        self.p_cr.plot_pixel(poi, label + " (pixel {})".format(poi))
        self.p_crwrr.set_path(path)
        self.p_crwrr.plot_pixel(poi, label + " (pixel {})".format(poi))
        self.p_mean.set_path(path)
        self.p_mean.plot_pixel(poi, label + " (pixel {})".format(poi))

    def plot_camera(self, file, label):
        path = file.charge_resolution_path

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
    poi = 888

    output_dir = get_plot("charge_resolution/lab_vs_mc")
    path_dict = {
        "MC-Lab 0MHz": MCLab_Opct40_0MHz(),
        "MC-Lab 5MHz": MCLab_Opct40_5MHz(),
        "MC-Lab 125MHz": MCLab_Opct40_125MHz(),
        "Lab (TF-Poly)": Lab_TFPoly(),
    }
    ph = PlotHandler()
    ph.plot_pixel_from_dict(path_dict, poi)
    ph.save(output_dir)

    output_dir = get_plot("charge_resolution/tf_comparison")
    path_dict = {
        "Lab (No TF)": Lab_TFNone(),
        "Lab (TF-PCHIP)": Lab_TFPchip(),
        "Lab (TF-Poly)": Lab_TFPoly(),
        "Lab (TF-WithPedestal)": Lab_TFWithPed(),
    }
    ph = PlotHandler()
    ph.plot_pixel_from_dict(path_dict, poi)
    ph.save(output_dir)

    output_dir = get_plot("charge_resolution/50ADC_vs_100ADC_vs_200ADC")
    path_dict = {
        "Lab 200ADV-GM (TF-Poly)": Lab_GM200ADC(),
        "Lab 100ADC-GM (TF-Poly)": Lab_GM100ADC(),
        "Lab 50ADC-GM (TF-Poly)": Lab_GM50ADC(),
    }
    ph = PlotHandler()
    ph.plot_pixel_from_dict(path_dict, poi)
    ph.save(output_dir)

    output_dir = get_plot("charge_resolution/checm_vs_checs")
    path_dict = {
        "CHEC-M": CHECM(),
        "CHEC-S (TF-Poly)": Lab_TFPoly(),
    }
    ph = PlotHandler()
    ph.plot_pixel_from_dict(path_dict, poi)
    ph.save(output_dir)


if __name__ == '__main__':
    main()

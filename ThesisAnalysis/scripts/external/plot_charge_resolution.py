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

    def save(self, output_dir, loc="best"):
        true = np.geomspace(0.1, 2000, 1000)
        self.p_cr.plot_requirement(true)
        self.p_cr.plot_poisson(true)
        self.p_cr.add_legend(loc)
        self.p_crwrr.plot_requirement(true)
        self.p_crwrr.plot_poisson(true)
        self.p_crwrr.add_legend(loc)
        self.p_mean.add_legend(loc)

        self.p_cr.save(os.path.join(output_dir, "charge_res.pdf"))
        self.p_crwrr.save(os.path.join(output_dir, "charge_res_wrr.pdf"))
        self.p_mean.save(os.path.join(output_dir, "charge_mean.pdf"))


def main():
    poi = 888

    # output_dir = get_plot("charge_resolution/lab_vs_mc")
    # path_dict = {
    #     "MC-Lab 0MHz": MCLab_Opct40_0MHz(),
    #     "MC-Lab 5MHz": MCLab_Opct40_5MHz(),
    #     "MC-Lab 125MHz": MCLab_Opct40_125MHz(),
    #     "Lab (TF-Poly)": Lab_TFPoly(),
    # }
    # ph = PlotHandler()
    # ph.plot_pixel_from_dict(path_dict, poi)
    # ph.save(output_dir)
    #
    # output_dir = get_plot("charge_resolution/tf_comparison")
    # path_dict = {
    #     "Lab (No TF)": Lab_TFNone(),
    #     "Lab (TF-PCHIP)": Lab_TFPchip(),
    #     "Lab (TF-Poly)": Lab_TFPoly(),
    #     "Lab (TF-WithPedestal)": Lab_TFWithPed(),
    # }
    # ph = PlotHandler()
    # ph.plot_pixel_from_dict(path_dict, poi)
    # ph.save(output_dir)
    #
    # output_dir = get_plot("charge_resolution/50ADC_vs_100ADC_vs_200ADC")
    # path_dict = {
    #     "Lab 200ADV-GM (TF-Poly)": Lab_GM200ADC(),
    #     "Lab 100ADC-GM (TF-Poly)": Lab_GM100ADC(),
    #     "Lab 50ADC-GM (TF-Poly)": Lab_GM50ADC(),
    # }
    # ph = PlotHandler()
    # ph.plot_pixel_from_dict(path_dict, poi)
    # ph.save(output_dir)
    #
    # output_dir = get_plot("charge_resolution/checm_vs_checs")
    # path_dict = {
    #     "CHEC-M": CHECM(),
    #     "CHEC-S (TF-Poly)": Lab_TFPoly(),
    # }
    # ph = PlotHandler()
    # ph.plot_pixel_from_dict(path_dict, poi)
    # ph.save(output_dir)

    # output_dir = get_plot("charge_resolution/opct_comparison")
    # path_dict = {
    #     "OPCT40, 5MHz": MCLab_Opct40_5MHz(),
    #     "OPCT40, 125MHz": MCLab_Opct40_125MHz(),
    #     "OPCT20, 5MHz": MCLab_Opct20_5MHz(),
    #     "OPCT20, 125MHz": MCLab_Opct20_125MHz(),
    # }
    # ph = PlotHandler()
    # ph.plot_pixel_from_dict(path_dict, poi)
    # ph.save(output_dir)

    # output_dir = get_plot("charge_resolution/charge_extraction_comparison")
    # path_dict = {
    #     # "CC, 5MHz": MCLab_Opct40_5MHz(),
    #     # "CC, 125MHz": MCLab_Opct40_125MHz(),
    #     # "Window, 5MHz": MCLab_Opct40_Window_5MHz(),
    #     # "Window, 125MHz": MCLab_Opct40_Window_125MHz(),
    #     "CC, 5MHz": MCLab_Opct20_5MHz(),
    #     "Window, 5MHz": MCLab_Opct20_Window_5MHz(),
    #     "Window, 125MHz": MCLab_Opct20_Window_125MHz(),
    #     # "CC, 5MHz, mc_true": MCLab_Opct40_5MHz(mc_true=True),
    #     # "CC, 125MHz, mc_true": MCLab_Opct40_125MHz(mc_true=True),
    #     # "Window, 5MHz, mc_true": MCLab_Opct40_Window_5MHz(mc_true=True),
    #     # "Window, 125MHz, mc_true": MCLab_Opct40_Window_125MHz(mc_true=True),
    # }
    # ph = PlotHandler()
    # ph.plot_pixel_from_dict(path_dict, poi)
    # ph.save(output_dir)

    # output_dir = get_plot("charge_resolution/mc_calibration")
    # path_dict = {
    #     "Default Calibration, 5MHz": MCLab_Opct40_5MHz(),
    #     "MC Calibration, 5MHz": MCLab_Opct40_5MHz(mc_true=True),
    #     "Default Calibration, 125MHz": MCLab_Opct40_125MHz(),
    #     "MC Calibration, 125MHz": MCLab_Opct40_125MHz(mc_true=True),
    # }
    # ph = PlotHandler()
    # ph.plot_pixel_from_dict(path_dict, poi)
    # ph.save(output_dir)


    output_dir = get_plot("charge_resolution/ce_comparison/lab")
    path_dict = {
        "Cross-Correlation": Lab_TFPoly(),
        "Window Integration": Lab_Window(),
    }
    ph = PlotHandler()
    ph.plot_pixel_from_dict(path_dict, poi)
    ph.save(output_dir)

    # output_dir = get_plot("charge_resolution/ce_comparison/opct40")
    # path_dict = {
    #     "Cross-Correlation, 5MHz": MCLab_Opct40_5MHz(),
    #     "Window Integration, 5MHz": MCLab_Opct40_Window_5MHz(),
    #     "Cross-Correlation, 125MHz": MCLab_Opct40_125MHz(),
    #     "Window Integration, 125MHz": MCLab_Opct40_Window_125MHz(),
    # }
    # ph = PlotHandler()
    # ph.plot_pixel_from_dict(path_dict, poi)
    # ph.save(output_dir)

    # output_dir = get_plot("charge_resolution/ce_comparison/opct20")
    # path_dict = {
    #     "Cross-Correlation, 5MHz": MCLab_Opct20_5MHz(),
    #     "Window Integration, 5MHz": MCLab_Opct20_Window_5MHz(),
    #     "Cross-Correlation, 125MHz": MCLab_Opct20_125MHz(),
    #     "Window Integration, 125MHz": MCLab_Opct20_Window_125MHz(),
    # }
    # ph = PlotHandler()
    # ph.plot_pixel_from_dict(path_dict, poi)
    # ph.save(output_dir)

    # output_dir = get_plot("charge_resolution/ce_comparison/high_noise")
    # path_dict = {
    #     "Cross-Correlation": MCLab_Opct20_CC_5MHz_HEN(),
    #     "Window Integration": MCLab_Opct20_Window_5MHz_HEN(),
    # }
    # ph = PlotHandler()
    # ph.plot_pixel_from_dict(path_dict, poi)
    # ph.save(output_dir)

    output_dir = get_plot("charge_resolution/ce_comparison/onsky")
    path_dict = {
        "CC Local Peak-Finding, 5MHz": MCOnSky_5MHz_CC_Local(mc_true=True),
        "CC Neighbour Peak-Finding, 5MHz": MCOnSky_5MHz_CC_Neighbour(mc_true=True),
        # "CC Local Peak-Finding, 125MHz": MCOnSky_125MHz_CC_Local(mc_true=True),
        # "CC Neighbour Peak-Finding, 125MHz": MCOnSky_125MHz_CC_Neighbour(mc_true=True),
        "Window Local Peak-Finding, 5MHz": MCOnSky_5MHz_Window_Local(mc_true=True),
        "Window Neighbour Peak-Finding, 5MHz": MCOnSky_5MHz_Window_Neighbour(mc_true=True),
        # "Window Local Peak-Finding, 125MHz": MCOnSky_125MHz_Window_Local(mc_true=True),
        # "Window Neighbour Peak-Finding, 125MHz": MCOnSky_125MHz_Window_Neighbour(mc_true=True),
    }
    ph = PlotHandler()
    ph.plot_pixel_from_dict(path_dict, poi)
    ph.save(output_dir)


if __name__ == '__main__':
    main()

from ThesisAnalysis.plotting.resolutions import ChargeResolutionPlotter, \
    ChargeResolutionWRRPlotter, ChargeMeanPlotter
from ThesisAnalysis.files import *
from ThesisAnalysis import get_plot, ThesisHDF5Reader, get_data
import os
import numpy as np


class PlotHandler:
    def __init__(self, plot_yerr=True, plot_xerr=True, **kwargs):
        kwargs2 = dict(plot_yerr=plot_yerr, plot_xerr=plot_xerr, **kwargs)
        self.p_cr = ChargeResolutionPlotter(**kwargs2)
        self.p_crwrr = ChargeResolutionWRRPlotter(**kwargs2)
        self.p_mean = ChargeMeanPlotter(**kwargs)

        true = np.geomspace(0.1, 1000, 100)
        self.p_cr.plot_requirement(true)
        self.p_cr.plot_poisson(true)
        self.p_crwrr.plot_requirement(true)
        self.p_crwrr.plot_poisson(true)

    def plot_pixel(self, file, label, poi):
        path = file.charge_resolution_path
        dead = file.dead

        self.p_cr.set_path(path, dead)
        self.p_cr.plot_pixel(poi, label)
        self.p_crwrr.set_path(path, dead)
        self.p_crwrr.plot_pixel(poi, label)
        self.p_mean.set_path(path)
        self.p_mean.plot_pixel(poi, label)

    def plot_camera(self, file, label):
        path = file.charge_resolution_path
        dead = file.dead

        self.p_cr.set_path(path, dead)
        self.p_cr.plot_camera(label)
        self.p_crwrr.set_path(path, dead)
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
        self.p_cr.add_legend(loc)
        self.p_crwrr.add_legend(loc)
        self.p_mean.add_legend(loc)

        self.p_cr.save(os.path.join(output_dir, "charge_res.pdf"))
        self.p_crwrr.save(os.path.join(output_dir, "charge_res_wrr.pdf"))
        self.p_mean.save(os.path.join(output_dir, "charge_mean.pdf"))


def main():
    poi = 888

    output_dir = get_plot("charge_resolution/1_lab")
    path_dict = {
        "Lab": Lab_TFPoly(),
    }
    ph = PlotHandler()
    ph.plot_pixel_from_dict(path_dict, poi)
    ph.save(output_dir)

    output_dir = get_plot("charge_resolution/2_lab_vs_mc")
    path_dict = {
        "Lab": Lab_TFPoly(),
        "MCLab": MCLab_Opct40_5MHz(),
        "MCLabTrue": MCLab_Opct40_5MHz(mc_true=True),
        "MCOnsky": MCOnSky_5MHz_CC_Local(mc_true=True),
    }
    ph = PlotHandler()
    ph.plot_pixel_from_dict(path_dict, poi)
    ph.p_crwrr.ax.set_ylim(top=1.2)
    ph.p_crwrr.ax.set_xlabel("Average Expected Charge (or True Charge) (p.e.)")
    ph.save(output_dir)

    output_dir = get_plot("charge_resolution/3_nsb_comparison/MCLab")
    path_dict = {
        "0MHz": MCLab_Opct40_0MHz(),
        "5MHz": MCLab_Opct40_5MHz(),
        "40MHz": MCLab_Opct40_40MHz(),
        "125MHz": MCLab_Opct40_125MHz(),
        "1200MHz": MCLab_Opct40_1200MHz(),
    }
    ph = PlotHandler()
    ph.plot_pixel_from_dict(path_dict, poi)
    ph.save(output_dir)

    output_dir = get_plot("charge_resolution/3_nsb_comparison/MCLabTrue")
    path_dict = {
        "0MHz": MCLab_Opct40_0MHz(mc_true=True),
        "5MHz": MCLab_Opct40_5MHz(mc_true=True),
        "40MHz": MCLab_Opct40_40MHz(mc_true=True),
        "125MHz": MCLab_Opct40_125MHz(mc_true=True),
        "1200MHz": MCLab_Opct40_1200MHz(mc_true=True),
    }
    ph = PlotHandler()
    ph.plot_pixel_from_dict(path_dict, poi)
    ph.p_crwrr.ax.set_xlabel("True Charge (p.e.)")
    ph.save(output_dir)

    output_dir = get_plot("charge_resolution/3_nsb_comparison/MCOnsky")
    path_dict = {
        "5MHz": MCOnSky_5MHz_CC_Local(mc_true=True),
        "125MHz": MCOnSky_125MHz_CC_Local(mc_true=True),
    }
    ph = PlotHandler()
    ph.plot_pixel_from_dict(path_dict, poi)
    ph.p_crwrr.ax.set_xlabel("True Charge (p.e.)")
    ph.save(output_dir)


    output_dir = get_plot("charge_resolution/4_opct/mc")
    path_dict = {
        # "OPCT40, 5MHz": MCLab_Opct40_5MHz(),
        "40% OPCT": MCLab_Opct40_125MHz(),
        # "OPCT20, 5MHz": MCLab_Opct20_5MHz(),
        "20% OPCT": MCLab_Opct20_125MHz(),
    }
    ph = PlotHandler()
    ph.plot_pixel_from_dict(path_dict, poi)
    ph.save(output_dir)

    output_dir = get_plot("charge_resolution/4_opct/biasvoltage")
    path_dict = {
        "200ADC-GM": Lab_GM200ADC(),
        "100ADC-GM": Lab_GM100ADC(),
        "50ADC-GM": Lab_GM50ADC(),
    }
    ph = PlotHandler(plot_yerr=False)
    ph.plot_pixel_from_dict(path_dict, poi)
    ph.p_crwrr.ax.set_ylim(top=1.2)
    ph.save(output_dir)

    output_dir = get_plot("charge_resolution/5_camera_comparison")
    path_dict = {
        "CHEC-S": Lab_TFPoly(),
        "CHEC-M": CHECM(),
    }
    ph = PlotHandler(switch_backend=True)
    ph.plot_pixel_from_dict(path_dict, poi)
    # ph.p_crwrr.ax.set_ylim(top=3)
    ph.save(output_dir)

    output_dir = get_plot("charge_resolution/6_tf_comparison")
    path_dict = {
        "Lab (No TF)": Lab_TFNone(),
        "Lab (TF-PCHIP)": Lab_TFPchip(),
        "Lab (TF-Poly)": Lab_TFPoly(),
        "Lab (TF-WithPedestal)": Lab_TFWithPed(),
    }
    ph = PlotHandler()
    ph.plot_pixel_from_dict(path_dict, poi)
    ph.p_crwrr.ax.set_ylim(top=3)
    ph.save(output_dir)

    output_dir = get_plot("charge_resolution/7_fit")
    path_dict = {
        "Data": Lab_TFPoly(),
    }
    ph = PlotHandler()
    ph.plot_pixel_from_dict(path_dict, poi)
    with ThesisHDF5Reader(get_data("charge_res_fit.h5")) as reader:
        df = reader.read('data')
        x = df['x'].values
        y = df['y'].values
        ynsb = df['ynsb'].values
        yopct_geo = df['yopct_geo'].values
        yopct_branching = df['yopct_branching'].values
    yreq = ph.p_crwrr.requirement(x)
    ph.p_crwrr.ax.plot(x, y/yreq, label='Fit')
    ph.p_crwrr.ax.plot(x, ynsb/yreq, label='125MHz')
    ph.p_crwrr.ax.plot(x, yopct_geo/yreq, label='10% OPCT (Geometry)')
    ph.p_crwrr.ax.plot(x, yopct_branching/yreq, label='10% OPCT (Branching)')
    ph.p_crwrr.ax.set_ylim(top=1.2)
    ph.save(output_dir)





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


    # output_dir = get_plot("charge_resolution/ce_comparison/lab")
    # path_dict = {
    #     "Cross-Correlation": Lab_TFPoly(),
    #     "Window Integration": Lab_Window(),
    # }
    # ph = PlotHandler()
    # ph.plot_pixel_from_dict(path_dict, poi)
    # ph.save(output_dir)
    #
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
    #
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
    #
    # output_dir = get_plot("charge_resolution/ce_comparison/high_noise")
    # path_dict = {
    #     "Cross-Correlation": MCLab_Opct20_CC_5MHz_HEN(),
    #     "Window Integration": MCLab_Opct20_Window_5MHz_HEN(),
    # }
    # ph = PlotHandler()
    # ph.plot_pixel_from_dict(path_dict, poi)
    # ph.save(output_dir)
    #
    # output_dir = get_plot("charge_resolution/ce_comparison/onsky")
    # path_dict = {
    #     # "CC Local Peak-Finding, 5MHz": MCOnSky_5MHz_CC_Local(mc_true=True),
    #     # "CC Neighbour Peak-Finding, 5MHz": MCOnSky_5MHz_CC_Neighbour(mc_true=True),
    #     "CC Local Peak-Finding, 125MHz": MCOnSky_125MHz_CC_Local(mc_true=True),
    #     "CC Neighbour Peak-Finding, 125MHz": MCOnSky_125MHz_CC_Neighbour(mc_true=True),
    #     # "Window Local Peak-Finding, 5MHz": MCOnSky_5MHz_Window_Local(mc_true=True),
    #     # "Window Neighbour Peak-Finding, 5MHz": MCOnSky_5MHz_Window_Neighbour(mc_true=True),
    #     "Window Local Peak-Finding, 125MHz": MCOnSky_125MHz_Window_Local(mc_true=True),
    #     "Window Neighbour Peak-Finding, 125MHz": MCOnSky_125MHz_Window_Neighbour(mc_true=True),
    # }
    # ph = PlotHandler()
    # ph.plot_pixel_from_dict(path_dict, poi)
    # ph.save(output_dir)


if __name__ == '__main__':
    main()

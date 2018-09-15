from ThesisAnalysis.plotting.resolutions import ChargeResolutionPlotter, \
    ChargeResolutionWRRPlotter, ChargeMeanPlotter
from ThesisAnalysis.files import *
from ThesisAnalysis import get_plot, ThesisHDF5Reader, get_data
import os
import numpy as np


class PlotHandler:
    def __init__(self, **kwargs):
        self.p_cr = ChargeResolutionPlotter(**kwargs)
        self.p_crwrr = ChargeResolutionWRRPlotter(**kwargs)
        self.p_mean = ChargeMeanPlotter(**kwargs)

        true = np.geomspace(0.1, 1000, 100)
        self.p_cr.plot_requirement(true)
        self.p_cr.plot_poisson(true)
        self.p_crwrr.plot_requirement(true)
        self.p_crwrr.plot_poisson(true)

    def plot_average(self, file, label, poi, n_bins=40):
        self.p_cr.set_file(file)
        self.p_cr.plot_average(label, n_bins)
        self.p_crwrr.set_file(file)
        self.p_crwrr.plot_average(label, n_bins)

        self.p_mean.set_path(file.charge_resolution_path)
        self.p_mean.plot_pixel(poi, label)

    def plot_pixel(self, file, label, poi):
        self.p_cr.set_file(file)
        self.p_cr.plot_pixel(poi, label)
        self.p_crwrr.set_file(file)
        self.p_crwrr.plot_pixel(poi, label)
        self.p_mean.set_path(file.charge_resolution_path)
        self.p_mean.plot_pixel(poi, label)

    def plot_camera(self, file, label):
        self.p_cr.set_file(file)
        self.p_cr.plot_camera(label)
        self.p_crwrr.set_file(file)
        self.p_crwrr.plot_camera(label)
        self.p_mean.set_path(file.charge_resolution_path)
        self.p_mean.plot_camera(label)

    def plot_average_from_dict(self, path_dict, poi):
        for label, path in path_dict.items():
            self.plot_average(path, label, poi)

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

    # output_dir = get_plot("charge_resolution/1_lab")
    # path_dict = {
    #     "Lab": Lab_TFPoly(),
    # }
    # ph = PlotHandler()
    # ph.plot_average_from_dict(path_dict, poi)
    # ph.save(output_dir)
    #
    # output_dir = get_plot("charge_resolution/2_lab_vs_mc")
    # path_dict = {
    #     "Lab": Lab_TFPoly(),
    #     "MCLab": MCLab_Opct40_5MHz(),
    #     "MCLabTrue": MCLab_Opct40_5MHz(mc_true=True),
    #     "MCOnsky": MCOnSky_5MHz_CC_Local(mc_true=True),
    # }
    # ph = PlotHandler()
    # ph.plot_average_from_dict(path_dict, poi)
    # ph.p_crwrr.ax.set_ylim(top=1.5)
    # ph.p_crwrr.ax.set_xlabel("Average Expected Charge (or True Charge) (p.e.)")
    # ph.save(output_dir)
    #
    # output_dir = get_plot("charge_resolution/3_nsb_comparison/MCLab")
    # path_dict = {
    #     "0MHz": MCLab_Opct40_0MHz(),
    #     "5MHz": MCLab_Opct40_5MHz(),
    #     "40MHz": MCLab_Opct40_40MHz(),
    #     "125MHz": MCLab_Opct40_125MHz(),
    #     "1200MHz": MCLab_Opct40_1200MHz(),
    # }
    # ph = PlotHandler()
    # ph.plot_average_from_dict(path_dict, poi)
    # ph.save(output_dir)
    #
    # output_dir = get_plot("charge_resolution/3_nsb_comparison/MCLabTrue")
    # path_dict = {
    #     "0MHz": MCLab_Opct40_0MHz(mc_true=True),
    #     "5MHz": MCLab_Opct40_5MHz(mc_true=True),
    #     "40MHz": MCLab_Opct40_40MHz(mc_true=True),
    #     "125MHz": MCLab_Opct40_125MHz(mc_true=True),
    #     "1200MHz": MCLab_Opct40_1200MHz(mc_true=True),
    # }
    # ph = PlotHandler()
    # ph.plot_average_from_dict(path_dict, poi)
    # ph.p_crwrr.ax.set_xlabel("True Charge (p.e.)")
    # ph.save(output_dir)
    #
    # output_dir = get_plot("charge_resolution/3_nsb_comparison/MCOnsky")
    # path_dict = {
    #     "5MHz": MCOnSky_5MHz_CC_Local(mc_true=True),
    #     "125MHz": MCOnSky_125MHz_CC_Local(mc_true=True),
    # }
    # ph = PlotHandler()
    # ph.plot_average_from_dict(path_dict, poi)
    # ph.p_crwrr.ax.set_xlabel("True Charge (p.e.)")
    # ph.save(output_dir)
    #
    #
    # output_dir = get_plot("charge_resolution/4_opct/mc")
    # path_dict = {
    #     # "OPCT40, 5MHz": MCLab_Opct40_5MHz(),
    #     "40% OPCT": MCLab_Opct40_125MHz(),
    #     # "OPCT20, 5MHz": MCLab_Opct20_5MHz(),
    #     "20% OPCT": MCLab_Opct20_125MHz(),
    # }
    # ph = PlotHandler()
    # ph.plot_average_from_dict(path_dict, poi)
    # ph.save(output_dir)
    #
    # output_dir = get_plot("charge_resolution/4_opct/biasvoltage")
    # path_dict = {
    #     "200ADC-GM": Lab_GM200ADC(),
    #     "100ADC-GM": Lab_GM100ADC(),
    #     "50ADC-GM": Lab_GM50ADC(),
    # }
    # ph = PlotHandler()
    # ph.plot_pixel_from_dict(path_dict, poi)
    # ph.p_crwrr.ax.set_ylim(top=1.2)
    # ph.save(output_dir)
    #
    # output_dir = get_plot("charge_resolution/5_camera_comparison")
    # ph = PlotHandler(switch_backend=True)
    # ph.plot_average(Lab_TFPoly(), "CHEC-S", poi)
    # ph.plot_average(CHECM(), "CHEC-M", poi, 14)
    # with ThesisHDF5Reader(get_data("charge_res_fit_checm.h5")) as reader:
    #     df = reader.read('data')
    #     x = df['x'].values
    #     y = df['y'].values
    # yreq = ph.p_crwrr.requirement(x)
    # ph.p_crwrr.ax.plot(x, y/yreq, label='CHEC-M Fit')
    # ph.save(output_dir)
    #
    # output_dir = get_plot("charge_resolution/6_tf_comparison")
    # path_dict = {
    #     "Lab (No TF)": Lab_TFNone(),
    #     "Lab (TF-PCHIP)": Lab_TFPchip(),
    #     "Lab (TF-Poly)": Lab_TFPoly(),
    #     "Lab (TF-WithPedestal)": Lab_TFWithPed(),
    # }
    # ph = PlotHandler()
    # ph.plot_average_from_dict(path_dict, poi)
    # ph.p_crwrr.ax.set_ylim(top=3)
    # ph.save(output_dir)
    #
    # output_dir = get_plot("charge_resolution/7_fit/lab")
    # path_dict = {
    #     "Data": Lab_TFPoly(),
    # }
    # ph = PlotHandler()
    # ph.plot_average_from_dict(path_dict, poi)
    # with ThesisHDF5Reader(get_data("charge_res_fit.h5")) as reader:
    #     df = reader.read('data')
    #     x = df['x'].values
    #     y = df['y'].values
    #     ynsb = df['ynsb'].values
    #     yopct_geo = df['yopct_geo'].values
    #     yopct_branching = df['yopct_branching'].values
    # yreq = ph.p_crwrr.requirement(x)
    # ph.p_crwrr.ax.plot(x, y/yreq, label='Fit')
    # ph.p_crwrr.ax.plot(x, ynsb/yreq, label='125MHz')
    # ph.p_crwrr.ax.plot(x, yopct_geo/yreq, label='10% OPCT (Geometry)')
    # ph.p_crwrr.ax.plot(x, yopct_branching/yreq, label='10% OPCT (Branching)')
    # ph.p_crwrr.ax.set_ylim(top=1.5)
    # ph.save(output_dir)
    #
    # output_dir = get_plot("charge_resolution/7_fit/mc")
    # path_dict = {
    #     "Data": MCLab_Opct40_5MHz(),
    # }
    # ph = PlotHandler()
    # ph.plot_average_from_dict(path_dict, poi)
    # with ThesisHDF5Reader(get_data("charge_res_fit_mc.h5")) as reader:
    #     df = reader.read('data')
    #     x = df['x'].values
    #     y = df['y'].values
    #     ynsb = df['ynsb'].values
    #     yopct_geo = df['yopct_geo'].values
    #     yopct_branching = df['yopct_branching'].values
    # yreq = ph.p_crwrr.requirement(x)
    # ph.p_crwrr.ax.plot(x, y/yreq, label='Fit')
    # ph.p_crwrr.ax.plot(x, ynsb/yreq, label='125MHz')
    # ph.p_crwrr.ax.plot(x, yopct_geo/yreq, label='10% OPCT (Geometry)')
    # ph.p_crwrr.ax.plot(x, yopct_branching/yreq, label='10% OPCT (Branching)')
    # ph.p_crwrr.ax.set_ylim(top=1.5)
    # ph.save(output_dir)

    # output_dir = get_plot("charge_resolution/8_ce_comparison/lab")
    # path_dict = {
    #     "Cross-Correlation": Lab_TFPoly(),
    #     "Window Integration": Lab_Window(),
    # }
    # ph = PlotHandler()
    # ph.plot_average_from_dict(path_dict, poi)
    # ph.save(output_dir)
    #
    # output_dir = get_plot("charge_resolution/8_ce_comparison/opct40")
    # path_dict = {
    #     "Cross-Correlation, 5MHz": MCLab_Opct40_5MHz(),
    #     "Window Integration, 5MHz": MCLab_Opct40_Window_5MHz(),
    #     "Cross-Correlation, 125MHz": MCLab_Opct40_125MHz(),
    #     "Window Integration, 125MHz": MCLab_Opct40_Window_125MHz(),
    # }
    # ph = PlotHandler()
    # ph.plot_average_from_dict(path_dict, poi)
    # ph.save(output_dir)
    #
    # output_dir = get_plot("charge_resolution/8_ce_comparison/opct20")
    # path_dict = {
    #     "Cross-Correlation, 5MHz": MCLab_Opct20_5MHz(),
    #     "Window Integration, 5MHz": MCLab_Opct20_Window_5MHz(),
    #     "Cross-Correlation, 125MHz": MCLab_Opct20_125MHz(),
    #     "Window Integration, 125MHz": MCLab_Opct20_Window_125MHz(),
    # }
    # ph = PlotHandler()
    # ph.plot_average_from_dict(path_dict, poi)
    # ph.save(output_dir)

    output_dir = get_plot("charge_resolution/8_ce_comparison/high_noise")
    ph = PlotHandler()
    ph.plot_average(MCLab_Opct20_CC_5MHz_HEN(), "Cross-Correlation", poi, 20)
    ph.plot_average(MCLab_Opct20_Window_5MHz_HEN(), "Window Integration", poi, 20)
    ph.save(output_dir)


if __name__ == '__main__':
    main()

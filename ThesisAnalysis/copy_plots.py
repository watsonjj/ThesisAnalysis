from ThesisAnalysis import get_plot, get_thesis_figure
from shutil import copy2
import os


def copy(src, chapter, file=None):
    src = get_plot(src)
    if file is None:
        file = os.path.basename(src)
    copy2(src, get_thesis_figure(chapter, file))


def copyex(src, chapter, file=None):
    if file is None:
        file = os.path.basename(src)
    copy2(src, get_thesis_figure(chapter, file))


# copy("charge_extraction_window/amp1nsb5.pdf", "a3")
# copy("charge_extraction_window/amp1nsb125.pdf", "a3")
# copy("charge_extraction_window/amp50nsb5.pdf", "a3")
# copy("charge_extraction_window/amp50nsb125.pdf", "a3")
# copy("charge_extraction_window/charge_extraction_window_wf.pdf", "a3")
#
# copy("fw_correction/gain-matching-original/fw_correction.pdf", "ch2")
# copy("fw_correction/gain-matching-original/measured_versus_transmission.pdf", "ch2")
# copy("fw_position/fw_position_justus.pdf", "ch2")
#
# copy("before_after_gm_ff/before_after_gm.pdf", "ch5")
# copy("before_after_gm_ff/before_after_ff_50pe.pdf", "ch5")
# copy("before_after_gm_ff/before_after_ff_25pe.pdf", "ch5")
# copy("before_after_gm_ff/before_after_ff_100pe.pdf", "ch5")
# copy("before_after_gm_ff/ff_values_cropped.pdf", "ch5")
# copy("pedestal/checs/cellwf_15.pdf", "ch5")
# copy("pedestal/checs/rawwf_10.pdf", "ch5")
# copy("pedestal/checs/pedestal_hist.pdf", "ch5")
# copy("pedestal/r0_cherenkov_image_mirrored_cropped.pdf", "ch5")
# copy("pedestal/r1_cherenkov_image_mirrored_cropped.pdf", "ch5")
# copy("pedestal/r1pe_cherenkov_image_mirrored_cropped.pdf", "ch5")
# copy("tf/generation_t5.pdf", "ch5")
# copy("tf/generation_tc.pdf", "ch5")
# copy("tf/lookup_t5.pdf", "ch5")
# copy("tf/lookup_tc.pdf", "ch5")
# copy("pulse_raw_vs_pedestal.pdf", "ch5")
# copy("saturation_recovery.pdf", "ch5")
# copy("tf/tf_pulse_fit.pdf", "ch5")
# copy("spe_spectrum_comparison/checm_checs.pdf", "ch5", "spe_checm_checs.pdf")
# copy("time_corrections/lab/image_cropped.pdf", "ch5", "time_correction.pdf")
#
# copy("annotated_waveform/checs_3pe.pdf", "ch6", "annotated_wf_3pe.pdf")
# copy("cross_correlation/cc_tmax.pdf", "ch6")
# copy("cross_correlation/cc_tnsb.pdf", "ch6")
# copy("cross_correlation/cc_tnoise.pdf", "ch6")

# copy("spe_spectrum_comparison/mc_lab.pdf", "ch7", "spe_sim_lab.pdf")
# copy("measured_vs_expected/checs/measured_vs_expected_hist.pdf", "ch7", "checs_mve_hist.pdf")
# copy("measured_vs_expected/checs/measured_vs_expected_scatter.pdf", "ch7", "checs_mve_scatter.pdf")
# copy("charge_resolution/1_lab/charge_res.pdf", "ch7", "cr_1_lab_raw.pdf")
# copy("charge_resolution/1_lab/charge_res_wrr.pdf", "ch7", "cr_1_lab.pdf")
# copy("charge_resolution/2_lab_vs_mc/charge_res_wrr.pdf", "ch7", "cr_2_lab_vs_mc.pdf")
# copy("charge_resolution/3_nsb_comparison/MCLab/charge_res_wrr.pdf", "ch7", "cr_3_nsb_comparison_mclab.pdf")
# copy("charge_resolution/3_nsb_comparison/MCLabTrue/charge_res_wrr.pdf", "ch7", "cr_3_nsb_comparison_mclabtrue.pdf")
# copy("charge_resolution/3_nsb_comparison/MCOnsky/charge_res_wrr.pdf", "ch7", "cr_3_nsb_comparison_mconsky.pdf")
# copy("charge_resolution/4_opct/mc/charge_res_wrr.pdf", "ch7", "cr_4_opct_mc.pdf")
# copy("charge_resolution/4_opct/biasvoltage/charge_res_wrr.pdf", "ch7", "cr_4_opct_biasvoltage.pdf")
# copy("charge_resolution/5_camera_comparison/charge_res_wrr.pdf", "ch7", "cr_5_camera_comparison.pdf")
# copy("charge_resolution/6_tf_comparison/charge_res_wrr.pdf", "ch7", "cr_6_tf_comparison.pdf")
# copy("charge_resolution/7_fit/lab/charge_res_wrr.pdf", "ch7", "cr_7_fit.pdf")
copy("charge_resolution/8_ce_comparison/lab/charge_res_wrr.pdf", "ch7", "cr_8_ce_comparison_lab.pdf")
copy("charge_resolution/8_ce_comparison/opct40/charge_res_wrr.pdf", "ch7", "cr_8_ce_comparison_opct40.pdf")
copy("charge_resolution/8_ce_comparison/opct20/charge_res_wrr.pdf", "ch7", "cr_8_ce_comparison_opct20.pdf")
copy("charge_resolution/8_ce_comparison/high_noise/charge_res_wrr.pdf", "ch7", "cr_8_ce_comparison_high_noise.pdf")
# copy("pulse_shape/pulse_shape_lab.pdf", "ch7")
# copy("pulse_shape/pulse_shape_mc.pdf", "ch7")
# copy("pulse_shape/pulse_shape_checm.pdf", "ch7")
# copy("measured_vs_expected/checm/measured_vs_expected_scatter.pdf", "ch7", "checm_mve_scatter.pdf")







# copy("measured_vs_expected/checm/measured_vs_expected_hist.pdf", "ch7", "checm_mve_hist.pdf")
# copy("measured_vs_expected/checm/measured_vs_expected_scatter.pdf", "ch7", "checm_mve_scatter.pdf")
#
#
# # External
# #
# copyex("/Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_poly/fw_calibration.pdf", "ch2")
# copyex("/Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_poly/fw_calibration_fit.pdf", "ch2")
#
# copyex("/Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_poly/flat_fielding.pdf", "ch5")
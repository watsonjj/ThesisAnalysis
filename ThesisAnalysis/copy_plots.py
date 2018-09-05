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
#
# copy("fw_correction/gain-matching-original/fw_correction.pdf", "ch2")
# copy("fw_correction/gain-matching-original/measured_versus_transmission.pdf", "ch2")
# copy("fw_position/fw_position_justus.pdf", "ch2")
#
# copy("before_after_gm_ff/before_after_gm.pdf", "ch5")
# copy("before_after_gm_ff/before_after_ff.pdf", "ch5")
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
copy("spe_spectrum_comparison/checm_checs.pdf", "ch5", "spe_checm_checs.pdf")

# copy("annotated_waveform/checs_3pe.pdf", "ch6", "annotated_wf_3pe.pdf")
# copy("cross_correlation/cc_tmax.pdf", "ch6")
# copy("cross_correlation/cc_tnsb.pdf", "ch6")
# copy("cross_correlation/cc_tnoise.pdf", "ch6")


# External
#
# copyex("/Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_poly/fw_calibration.pdf", "ch2")
#
# copyex("/Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_poly/flat_fielding.pdf", "ch5")
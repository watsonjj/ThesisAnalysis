#!/usr/bin/env python3
from subprocess import call
import os
import shutil
from glob import glob
import re
from ThesisAnalysis.scripts import external
from ThesisAnalysis.scripts import reduction
from ThesisAnalysis.scripts import analysis
from ThesisAnalysis.files import fw_correction_original_files as orginal
from ThesisAnalysis.files import fw_correction_post_files as post
from ThesisAnalysis.files import *


def process_illumination_profiles():
    reduction.mc_illumination_profile.main()
    analysis.mc_illumination_profile.main()


def process_fw_correction():
    [external.fw_calibration.process(f) for f in orginal]
    [external.charge_averages.process(f) for f in orginal]
    [external.flat_fielding.process(f) for f in orginal]
    [external.charge_before_after.process(f) for f in orginal]
    file_dict = {
        "50ADC-GM": Lab_GM50ADC_Original(),
        "100ADC-GM": Lab_GM100ADC_Original(),
        "200ADC-GM": Lab_GM200ADC_Original(),
    }
    external.fw_correction.process(file_dict, "gain-matching-original")
    os.remove("/Volumes/gct-jason/thesis_data/checs/lab/dynrange/runlist.txt")
    shutil.copy("/Users/Jason/Software/ThesisAnalysis/ThesisAnalysis/plots/"
                "fw_correction/gain-matching-original/runlist_new.txt",
                "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/runlist.txt")
    cmd = "python /Volumes/gct-jason/thesis_data/checs/lab/dynrange/gain/tf_poly/create_runlist.py"
    call(cmd, shell=True)


def process_fw_correction_check():
    [external.fw_calibration.process(f) for f in post]
    [external.charge_averages.process(f) for f in post]
    [external.flat_fielding.process(f) for f in post]
    [external.charge_before_after.process(f) for f in post]
    file_dict = {
        "50ADC-GM": Lab_GM50ADC(),
        "100ADC-GM": Lab_GM100ADC(),
        "200ADC-GM": Lab_GM200ADC(),
    }
    external.fw_correction.process(file_dict, "gain-matching-post")


def process_external():
    external.fw_calibration.main()
    external.charge_averages.main()
    external.flat_fielding.main()
    external.charge_before_after.main()
    external.fw_correction.main()
    external.charge_resolution.main()


def process_external_plots():
    external.plot_ff_charge_average.main()
    external.plot_charge_before_after.main()
    external.plot_charge_resolution.main()


def process_reduction():
    reduction.ff_values.main()
    reduction.before_after_gm.main()
    reduction.before_after_ff.main()
    reduction.cherenkov_pedestal_comparison.main()
    reduction.pedestal_residuals.main()
    reduction.saturation_recovery.main()
    reduction.spe_spectrum.main()
    reduction.spe_spectrum_checm.main()
    reduction.spe_spectrum_comparison.main()
    reduction.tf_generation.main()
    reduction.tf_lookup.main()


def process_analysis():
    analysis.before_after_gm_ff.main()
    analysis.cherenkov_pedestal_comparison.main()
    analysis.ff_versus_nsb.main()
    analysis.fw_position.main()
    analysis.pedestal_residuals.main()
    analysis.pulse_raw_vs_pedestal.main()
    analysis.saturation_recovery.main()
    analysis.spe_spectrum.main()
    analysis.spe_spectrum_comparison.main()
    analysis.tf_generation.main()
    analysis.tf_lookup.main()


def main():
    # process_illumination_profiles()
    # process_fw_correction()
    # process_fw_correction_check()
    process_external()
    process_external_plots()
    process_reduction()
    process_analysis()


if __name__ == '__main__':
    main()
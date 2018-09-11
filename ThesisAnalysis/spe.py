#!/usr/bin/env python3
from subprocess import call


def main():
    cmds = [
        # "python /Users/Jason/Software/CHECLabPy/scripts/extract_spe.py -f /Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/5mhz/Run43{514..516}_dl1.h5 -c /Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/5mhz/config.yml",
        # "python /Users/Jason/Software/CHECLabPy/scripts/extract_spe.py -f /Volumes/gct-jason/thesis_data/checs/mc/dynrange/4_opct20/5mhz/Run43{514..516}_dl1.h5 -c /Volumes/gct-jason/thesis_data/checs/mc/dynrange/4_opct20/5mhz/config.yml",
        # "python /Users/Jason/Software/CHECLabPy/scripts/extract_spe.py -f /Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/window_extractor/5mhz/Run43{514..516}_dl1.h5 -c /Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/window_extractor/5mhz/config.yml",
        # "python /Users/Jason/Software/CHECLabPy/scripts/extract_spe.py -f /Volumes/gct-jason/thesis_data/checs/mc/dynrange/4_opct20/window_extractor/5mhz/Run43{514..516}_dl1.h5 -c /Volumes/gct-jason/thesis_data/checs/mc/dynrange/4_opct20/window_extractor/5mhz/config.yml",
        # "python /Users/Jason/Software/CHECLabPy/scripts/extract_spe.py -f /Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_none/Run43{514..516}_dl1.h5 -c /Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_none/config.yml",
        # "python /Users/Jason/Software/CHECLabPy/scripts/extract_spe.py -f /Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_pchip/Run43{514..516}_dl1.h5",
        # "python /Users/Jason/Software/CHECLabPy/scripts/extract_spe.py -f /Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_poly/Run43{514..516}_dl1.h5",
        # "python /Users/Jason/Software/CHECLabPy/scripts/extract_spe.py -f /Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_withped/Run43{514..516}_dl1.h5",
        "python /Users/Jason/Software/CHECLabPy/scripts/extract_spe.py -f /Volumes/gct-jason/thesis_data/checs/lab/dynrange/gain/tf_poly/50ADC/Run175{53..55}_dl1.h5 -c /Volumes/gct-jason/thesis_data/checs/lab/dynrange/gain/tf_poly/50ADC/config.yml",
        "python /Users/Jason/Software/CHECLabPy/scripts/extract_spe.py -f /Volumes/gct-jason/thesis_data/checs/lab/dynrange/gain/tf_poly/100ADC/Run174{31..33}_dl1.h5 -c /Volumes/gct-jason/thesis_data/checs/lab/dynrange/gain/tf_poly/100ADC/config.yml",
        "python /Users/Jason/Software/CHECLabPy/scripts/extract_spe.py -f /Volumes/gct-jason/thesis_data/checs/lab/dynrange/gain/tf_poly/200ADC/Run174{92..94}_dl1.h5 -c /Volumes/gct-jason/thesis_data/checs/lab/dynrange/gain/tf_poly/200ADC/config.yml",
        # "python /Users/Jason/Software/CHECLabPy/scripts/extract_spe.py -f /Volumes/gct-jason/thesis_data/checs/lab/dynrange/window_extractor/Run43{514..516}_dl1.h5",
        # "python /Users/Jason/Software/CHECLabPy/scripts/extract_spe.py -f /Volumes/gct-jason/thesis_data/checm/spe/*_dl1.h5 -s MAPMFitter",
    ]
    for cmd in cmds:
        call(cmd, shell=True)


if __name__ == '__main__':
    main()
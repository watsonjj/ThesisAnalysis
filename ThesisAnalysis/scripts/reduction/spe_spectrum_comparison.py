from ThesisAnalysis import get_data, ThesisHDF5Writer
from ThesisAnalysis.files import MCLab_Opct40_5MHz, Lab_TFPoly
import numpy as np
import pandas as pd
from CHECLabPy.core.io import DL1Reader
from CHECLabPy.spectrum_fitters.gentile import GentileFitter
import warnings
from pandas.errors import PerformanceWarning


def get_dict(type, input_paths, config_path, roi, poi):
    readers = [DL1Reader(path) for path in input_paths]
    n_illuminations = len(readers)
    fitter = GentileFitter(n_illuminations, config_path)

    charges = []
    for reader in readers:
        pixel, charge = reader.select_columns(['pixel', 'charge'])
        if poi != -1:
            charge_p = charge[pixel == poi]
        else:
            charge_p = charge
        charges.append(charge_p)
    fitter.apply(*charges)

    eped = fitter.coeff['eped']
    spe = fitter.coeff['spe']
    charges_norm = [(c - eped) / spe for c in charges]

    fitter.range = [-1, 5]
    fitter.initial['eped_sigma'] = 0.5
    fitter.initial['spe'] = 1
    fitter.initial['spe_sigma'] = 0.1
    fitter.limits['limit_eped_sigma'] = [0.001, 1]
    fitter.limits['limit_spe'] = [0.001, 2]
    fitter.limits['limit_spe_sigma'] = [0.001, 1]
    fitter.apply(*charges_norm)

    fitx = np.linspace(fitter.range[0], fitter.range[1], 1000)
    coeff = fitter.coeff.copy()
    spe = coeff['spe']
    print(spe)

    return dict(
        type=type,
        edges=fitter.edges,
        between=fitter.between,
        fitx=fitx,
        hist=fitter.hist[roi],
        fit=fitter.fit_function(fitx, **coeff)[roi],
        roi=roi,
        **coeff
    )


def process(mc_file, mc_roi, lab_file, lab_roi):

    mc_input_paths = mc_file.spe_files
    mc_config_path = mc_file.spe_config_path
    poi = mc_file.poi
    lab_input_paths = lab_file.spe_files
    lab_config_path = lab_file.spe_config_path
    output_path = get_data("spe_spectrum_comparison.h5")

    d_list = list()
    d_list.append(get_dict("MC", mc_input_paths, mc_config_path, mc_roi, poi))
    d_list.append(get_dict("Lab", lab_input_paths, lab_config_path, lab_roi, poi))

    df = pd.DataFrame(d_list)

    with warnings.catch_warnings():
        warnings.simplefilter('ignore', PerformanceWarning)
        with ThesisHDF5Writer(output_path) as writer:
            writer.write(data=df)


def main():
    mc_file = MCLab_Opct40_5MHz()
    mc_roi = 2
    lab_file = Lab_TFPoly()
    lab_roi = 1
    process(mc_file, mc_roi, lab_file, lab_roi)


if __name__ == '__main__':
    main()

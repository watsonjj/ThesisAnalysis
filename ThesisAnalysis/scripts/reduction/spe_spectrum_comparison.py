from ThesisAnalysis import get_data, ThesisHDF5Writer
from ThesisAnalysis.files import MCLab_Opct40_5MHz, Lab_TFPoly, CHECM
import numpy as np
import pandas as pd
from CHECLabPy.core.io import DL1Reader
from CHECLabPy.spectrum_fitters.gentile import GentileFitter
from CHECLabPy.spectrum_fitters.mapm import MAPMFitter
import warnings
from pandas.errors import PerformanceWarning


def get_dict(type, input_paths, config_path, roi, poi, fitter):
    readers = [DL1Reader(path) for path in input_paths]
    n_illuminations = len(readers)
    fitter = fitter(n_illuminations, config_path)

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


def process(comparison_list, output_path):

    d_list = list()
    for d in comparison_list:
        name = d['name']
        file = d['file']
        roi = d['roi']
        fitter = d['fitter']

        input_paths = file.spe_files
        config_path = file.spe_config_path
        poi = file.poi

        d_list.append(get_dict(name, input_paths, config_path, roi, poi, fitter))

    df = pd.DataFrame(d_list)

    with warnings.catch_warnings():
        warnings.simplefilter('ignore', PerformanceWarning)
        with ThesisHDF5Writer(output_path) as writer:
            writer.write(data=df)


def main():
    comp = [
        dict(name="MC-Lab", file=MCLab_Opct40_5MHz(), roi=2, fitter=GentileFitter),
        dict(name="Lab", file=Lab_TFPoly(), roi=1, fitter=GentileFitter),
    ]
    output_path = get_data("spe_spectrum_comparison/mc_lab.h5")
    process(comp, output_path)

    comp = [
        dict(name="CHEC-M", file=CHECM(), roi=2, fitter=MAPMFitter),
        dict(name="CHEC-S", file=Lab_TFPoly(), roi=2, fitter=GentileFitter),
    ]
    output_path = get_data("spe_spectrum_comparison/checm_checs.h5")
    process(comp, output_path)


if __name__ == '__main__':
    main()

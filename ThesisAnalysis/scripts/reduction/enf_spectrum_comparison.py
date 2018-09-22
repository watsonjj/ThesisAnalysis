from ThesisAnalysis import get_data, ThesisHDF5Writer
from ThesisAnalysis.files import MCLab_Opct40_5MHz, Lab_TFPoly, CHECM
import numpy as np
import pandas as pd
from CHECLabPy.core.io import DL1Reader
from CHECLabPy.spectrum_fitters.gentile import GentileFitter
from CHECLabPy.spectrum_fitters.mapm import MAPMFitter
import warnings
from pandas.errors import PerformanceWarning
from scipy.special import binom
from math import factorial

C = np.sqrt(2.0 * np.pi)
FACTORIAL = np.array([factorial(i) for i in range(20)])
FACTORIAL_0 = FACTORIAL[0]
NPEAKS = 20
N = np.arange(NPEAKS)[:, None]
J = np.arange(NPEAKS)[None, :]
K = np.arange(1, NPEAKS)[:, None]
FACTORIAL_J_INV = 1 / FACTORIAL[J]
BINOM = binom(N - 1, J - 1)


def _normal_pdf(x, mean=0, std_deviation=1):
    u = (x - mean) / std_deviation
    return np.exp(-0.5 * u ** 2) / (C * std_deviation)


def _poisson_pmf_j(mu):
    return mu ** J * np.exp(-mu) * FACTORIAL_J_INV


def mapm_enf(x, norm, spe, spe_sigma, eped, eped_sigma, **kwargs):
    p = _poisson_pmf_j(0)[0]
    p[:] = 0
    p[1] = 1

    pe_sigma = np.sqrt(K * spe_sigma ** 2)

    signal = norm * p[K] * _normal_pdf(x, K * spe, pe_sigma)

    return signal.sum(0)


def sipm_enf(x, norm, eped, eped_sigma, spe, spe_sigma, lambda_, opct,
              pap, dap, **kwargs):

    pj = _poisson_pmf_j(0)
    pj[:] = 0
    pj[0, 1] = 1

    pct = np.sum(pj * np.power(1-opct, J) * np.power(opct, N - J) * BINOM, 1)

    sap = spe_sigma

    papk = np.power(1 - pap, N[:, 0])
    p0ap = pct * papk
    pap1 = pct * (1-papk) * papk

    pe_sigma = np.sqrt(K * spe_sigma ** 2)
    ap_sigma = np.sqrt(K * sap ** 2)

    signal = p0ap[K] * _normal_pdf(x, K * spe, pe_sigma)
    signal += pap1[K] * _normal_pdf(x, K * spe * (1.0-dap), ap_sigma)
    signal *= norm

    return signal.sum(0)


def get_dict(type, input_paths, config_path, roi, poi, fitter, func):
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

    fitx = np.linspace(-2, 8, 1000)
    coeff = fitter.coeff.copy()
    errors0 = fitter.errors.copy()
    errors = dict()
    for key, value in errors0.items():
        errors['error_' + key] = value
    spe = coeff['spe']
    print(spe)

    fitter._fit = func

    # from IPython import embed
    # embed()

    return dict(
        type=type,
        edges=fitter.edges,
        between=fitter.between,
        fitx=fitx,
        hist=fitter.hist[roi],
        fit=fitter.fit_function(fitx, **coeff)[roi],
        roi=roi,
        **coeff,
        **errors
    )


def process(comparison_list, output_path):

    d_list = list()
    for d in comparison_list:
        name = d['name']
        file = d['file']
        roi = d['roi']
        fitter = d['fitter']
        func = d['func']

        input_paths = file.spe_files
        config_path = file.spe_config_path
        poi = file.poi

        d_list.append(get_dict(name, input_paths, config_path, roi, poi, fitter, func))

    df = pd.DataFrame(d_list)

    with warnings.catch_warnings():
        warnings.simplefilter('ignore', PerformanceWarning)
        with ThesisHDF5Writer(output_path) as writer:
            writer.write(data=df)


def main():

    comp = [
        dict(name="CHEC-M", file=CHECM(), roi=2, fitter=MAPMFitter, func=mapm_enf),
        dict(name="CHEC-S", file=Lab_TFPoly(), roi=2, fitter=GentileFitter, func=sipm_enf),
    ]
    output_path = get_data("enf_spectrum_comparison/checm_checs.h5")
    process(comp, output_path)


if __name__ == '__main__':
    main()

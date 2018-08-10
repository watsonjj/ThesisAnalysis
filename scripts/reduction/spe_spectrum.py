from ThesisAnalysis import get_data, ThesisHDF5Writer
import numpy as np
import pandas as pd
from CHECLabPy.core.io import DL1Reader
from CHECLabPy.spectrum_fitters.gentile import GentileFitter
import warnings
from pandas.errors import PerformanceWarning


def process(input_paths, config_path, poi, output_path):
    readers = [DL1Reader(path) for path in input_paths]
    n_illuminations = len(readers)
    mapping = readers[0].mapping
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

    fitx = np.linspace(fitter.range[0], fitter.range[1], 1000)
    coeff = fitter.coeff.copy()

    d = dict(
        edges=fitter.edges,
        between=fitter.between,
        fitx=fitx
    )
    for i in range(n_illuminations):
        d["hist{}".format(i)] = fitter.hist[i]
        d["fit{}".format(i)] = fitter.fit_function(fitx, **coeff)[i]

    df_array = pd.DataFrame([d])
    df_coeff = pd.DataFrame(coeff, index=[0])

    with warnings.catch_warnings():
        warnings.simplefilter('ignore', PerformanceWarning)
        with ThesisHDF5Writer(output_path) as writer:
            writer.write(array=df_array, coeff=df_coeff)
            writer.write_mapping(mapping)
            writer.write_metadata({'n_illuminations': n_illuminations})


def main():
    # input_paths = [
    #     "/Volumes/gct-jason/mc_checs/dynamic_range/opct40/5mhz/Run43514_dl1.h5",
    #     "/Volumes/gct-jason/mc_checs/dynamic_range/opct40/5mhz/Run43515_dl1.h5",
    #     "/Volumes/gct-jason/mc_checs/dynamic_range/opct40/5mhz/Run43516_dl1.h5"
    # ]
    input_paths = [
        "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/5mhz/Run43514_dl1.h5",
        "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/5mhz/Run43515_dl1.h5",
        "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/5mhz/Run43516_dl1.h5"
    ]
    config_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/5mhz/config.yml"
    poi = 888
    output_path = get_data("mc_spe_spectrum.h5")
    process(input_paths, config_path, poi, output_path)

    # input_paths = [
    #     "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/5mhz/Run43514_dl1.h5",
    #     "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/5mhz/Run43515_dl1.h5",
    #     "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/5mhz/Run43516_dl1.h5"
    # ]
    # config_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/5mhz/config.yml"
    # poi = 888
    # output_name = get_data("mc_spe_spectrum.h5")
    # process(input_paths, config_path, poi, output_name)


if __name__ == '__main__':
    main()

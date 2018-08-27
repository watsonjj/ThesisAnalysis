from ThesisAnalysis import get_data, ThesisHDF5Writer
from ThesisAnalysis.files import spe_files
import numpy as np
import pandas as pd
from CHECLabPy.core.io import DL1Reader
from CHECLabPy.spectrum_fitters.gentile import GentileFitter
import warnings
from pandas.errors import PerformanceWarning


def process(file):

    name = file.__class__.__name__
    input_paths = file.spe_files
    config_path = file.spe_config_path
    poi = file.poi
    output_path = get_data("spe/{}_spe_spectrum.h5".format(name))

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
            writer.write_metadata(n_illuminations=n_illuminations)


def main():
    [process(f) for f in spe_files]


if __name__ == '__main__':
    main()

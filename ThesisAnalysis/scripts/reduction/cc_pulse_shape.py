from ThesisAnalysis import ThesisHDF5Writer, get_data, ThesisHDF5Reader
from ThesisAnalysis.files import Lab_TFPoly, MCLab_Opct40_5MHz, CHECM, MC
from CHECLabPy.utils.waveform import get_average_wf_per_pixel
from CHECLabPy.waveform_reducers.average_wf import AverageWF
from CHECLabPy.waveform_reducers.cross_correlation import CrossCorrelation
from CHECLabPy.core.io import ReaderR1
# from CHECLabPy.core.io_simtel import ReaderSimtel
import numpy as np
import pandas as pd
import os
from glob import glob
import re
from target_calib import CameraConfiguration
from IPython import embed


def process(file, output_path):
    df_runs = file.get_dataframe(r1=True, open_readers=False)
    dead = file.dead
    input_dir = os.path.dirname(df_runs.iloc[0]['path'])

    reader_class = ReaderR1
    input_path = os.path.join(input_dir, "Run{:05d}_r1.tio")

    first_reader = reader_class(input_path.format(df_runs.iloc[0].name))
    n_pixels = first_reader.n_pixels
    pixels = np.arange(n_pixels)
    pixels = pixels[~np.isin(pixels, dead)]
    n_pixels = pixels.size
    n_samples = first_reader.n_samples
    ref_path = first_reader.reference_pulse_path
    reducer = AverageWF(n_pixels, n_samples)
    cc = CrossCorrelation(n_pixels, n_samples,
                               reference_pulse_path=ref_path)

    df_list = []

    for run, row in df_runs.iterrows():
        path = input_path.format(run)
        reader = reader_class(path, max_events=1000)
        expected = row['expected']
        expected_err = row['expected_err']

        avgwf = get_average_wf_per_pixel(reader, 60)
        avgwf = avgwf[pixels]

        norm = np.trapz(avgwf, axis=1)
        avgwf_norm = avgwf / norm[:, None]

        params = reducer.process(avgwf_norm)

        tr = params['tr']
        fwhm = params['fwhm']
        charge = params['charge']

        params = cc.process(avgwf_norm)
        charge_cc = params['charge']

        df_list.append(pd.DataFrame(dict(
            expected=expected,
            expected_err=expected_err,
            tr=tr,
            fwhm=fwhm,
            charge=charge,
            charge_cc=charge_cc,
            pixel=pixels,
        )))

    df = pd.concat(df_list, ignore_index=True)

    with ThesisHDF5Writer(output_path) as writer:
        writer.write(data=df)


def main():
    file = Lab_TFPoly()
    output_path = get_data("cc_pulse_shape/pulse_shape_lab.h5")
    process(file, output_path)


if __name__ == '__main__':
    main()
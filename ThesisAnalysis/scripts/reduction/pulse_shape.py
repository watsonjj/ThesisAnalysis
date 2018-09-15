from ThesisAnalysis import ThesisHDF5Writer, get_data, ThesisHDF5Reader
from ThesisAnalysis.files import Lab_TFPoly, MCLab_Opct40_5MHz, CHECM, MC
from CHECLabPy.utils.waveform import get_average_wf_per_pixel
from CHECLabPy.waveform_reducers.average_wf import AverageWF
from CHECLabPy.waveform_reducers.cross_correlation import CrossCorrelation
from CHECLabPy.core.io import ReaderR1
from CHECLabPy.core.io_simtel import ReaderSimtel
import numpy as np
import pandas as pd
import os
from glob import glob
import re
from target_calib import CameraConfiguration
from IPython import embed


def commonsuffix(files):
    reveresed = [f[::-1] for f in files]
    return os.path.commonprefix(reveresed)[::-1]


def obtain_amplitude_from_filename(files):
    commonprefix = os.path.commonprefix
    pattern = commonprefix(files) + 'Amplitude_(.+?)' + commonsuffix(files)
    amplitudes = []
    for fp in files:
        try:
            reg_exp = re.search(pattern, fp)
            if reg_exp:
                amplitudes.append(int(reg_exp.group(1)))
        except AttributeError:
            print("Problem with Regular Expression, "
                  "{} does not match patten {}".format(fp, pattern))
    return amplitudes


def convert_mv_to_pe(amplitudes):
    ff = get_data("ff_values.h5")
    with ThesisHDF5Reader(ff) as reader:
        gamma_q = reader.read('data')['gamma_q'].values[0]
        gamma_qerr = reader.read('data')['gamma_q_err'].values[0]

    ref_path = CameraConfiguration("1.1.0").GetReferencePulsePath()
    cc = CrossCorrelation(1, 96, reference_pulse_path=ref_path)
    amplitudes_area = np.array(amplitudes) / cc.y_1pe.max()
    expected = amplitudes_area / gamma_q
    expected_err = amplitudes_area / (gamma_q**2 / gamma_qerr)
    return expected, expected_err


def process(file, output_path):
    df_runs = file.get_dataframe(r1=True, open_readers=False)
    dead = file.dead
    input_dir = os.path.dirname(df_runs.iloc[0]['path'])

    reader_class = ReaderR1
    input_path = os.path.join(input_dir, "Run{:05d}_r1.tio")
    if issubclass(file.__class__, MC):
        reader_class = ReaderSimtel
        input_path = os.path.join(input_dir, "run{:05d}.simtel.gz")

    first_reader = reader_class(input_path.format(df_runs.iloc[0].name))
    n_pixels = first_reader.n_pixels
    pixels = np.arange(n_pixels)
    pixels = pixels[~np.isin(pixels, dead)]
    n_pixels = pixels.size
    n_samples = first_reader.n_samples
    reducer = AverageWF(n_pixels, n_samples)

    df_list = []

    for run, row in df_runs.iterrows():
        path = input_path.format(run)
        reader = reader_class(path, max_events=1000)
        expected = row['expected']
        expected_err = row['expected_err']

        avgwf = get_average_wf_per_pixel(reader, 60)
        avgwf = avgwf[pixels]

        params = reducer.process(avgwf)

        tr = params['tr']
        fwhm = params['fwhm']

        df_list.append(pd.DataFrame(dict(
            expected=expected,
            expected_err=expected_err,
            tr=tr,
            fwhm=fwhm,
            pixel=pixels,
        )))

    df = pd.concat(df_list, ignore_index=True)

    with ThesisHDF5Writer(output_path) as writer:
        writer.write(data=df)


def process_tf(output_path):
    files = glob("/Volumes/gct-jason/thesis_data/checs/lab/tf/*_r1.tio")
    amplitudes = obtain_amplitude_from_filename(files)
    expected_a, expected_err_a = convert_mv_to_pe(amplitudes)

    first_reader = ReaderR1(files[0])
    n_pixels = first_reader.n_pixels
    pixels = np.arange(n_pixels)
    n_pixels = pixels.size
    n_samples = first_reader.n_samples
    reducer = AverageWF(n_pixels, n_samples)

    df_list = []

    for path, expected, expected_err in zip(files, expected_a, expected_err_a):
        reader = ReaderR1(path, max_events=1000)

        avgwf = get_average_wf_per_pixel(reader, 60)
        avgwf = avgwf[pixels]

        params = reducer.process(avgwf)

        tr = params['tr']
        fwhm = params['fwhm']

        df_list.append(pd.DataFrame(dict(
            expected=expected,
            expected_err=expected_err,
            tr=tr,
            fwhm=fwhm,
            pixel=pixels,
        )))

    df = pd.concat(df_list, ignore_index=True)

    with ThesisHDF5Writer(output_path) as writer:
        writer.write(data=df)



def main():
    # file = Lab_TFPoly()
    # output_path = get_data("pulse_shape/pulse_shape_lab.h5")
    # process(file, output_path)
    #
    # file = MCLab_Opct40_5MHz()
    # output_path = get_data("pulse_shape/pulse_shape_mc.h5")
    # process(file, output_path)
    #
    # file = CHECM()
    # output_path = get_data("pulse_shape/pulse_shape_checm.h5")
    # process(file, output_path)

    output_path = get_data("pulse_shape/pulse_shape_tfwf.h5")
    process_tf(output_path)

if __name__ == '__main__':
    main()
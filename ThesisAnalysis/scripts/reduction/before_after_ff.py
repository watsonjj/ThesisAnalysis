from ThesisAnalysis import get_data, ThesisHDF5Writer, ThesisHDF5Reader
from ThesisAnalysis.files import Lab_TFPoly
import numpy as np
import pandas as pd
from target_calib import CameraConfiguration
from CHECLabPy.core.io import DL1Reader
from IPython import embed
from CHECLabPy.utils.files import open_runlist_dl1


def process(file, output_path):

    runlist_path = file.runlist_path
    fw_path = file.fw_path
    ff_path = get_data("ff_values.h5")
    illumination_path = file.illumination_profile_path

    with ThesisHDF5Reader(fw_path) as reader:
        df_fw = reader.read("data")
        fw_m = df_fw['fw_m'].values

    with ThesisHDF5Reader(illumination_path) as reader:
        correction = reader.read("correction")['correction']

    df_runs = open_runlist_dl1(runlist_path, open_readers=False)
    transmission = 1 / df_runs['fw_atten'].values
    expected = transmission * (fw_m / correction)[0]
    input_path = df_runs['path'].iloc[np.argmin(np.abs(expected - 50))]

    with DL1Reader(input_path) as reader:
        pixel, charge = reader.select_columns(['pixel', 'charge'])
        df = pd.DataFrame(dict(
            pixel=pixel,
            charge=charge
        ))
        df_mean = df.groupby('pixel').mean()
        charge = df_mean['charge'].values
        n_pixels = reader.n_pixels
        n_samples = reader.n_samples
        cv = reader.metadata['camera_version']

    with ThesisHDF5Reader(ff_path) as reader:
        df = reader.read("data")
        gamma_q = df['gamma_q'].values
        gamma_ff = df['gamma_ff'].values

    with ThesisHDF5Reader(illumination_path) as reader:
        correction = reader.read("correction")['correction']

    before = charge / gamma_q
    after = charge * gamma_ff / gamma_q
    after_ip = after / correction

    df = pd.DataFrame(dict(
        before=before,
        after=after,
        after_ip=after_ip
    ))

    reference_pulse_path = CameraConfiguration(cv).GetReferencePulsePath()

    with ThesisHDF5Writer(output_path) as writer:
        writer.write(data=df)
        writer.write_metadata(
            n_pixels=n_pixels,
            n_samples=n_samples,
            reference_pulse_path=reference_pulse_path
        )


def main():
    file = Lab_TFPoly()
    output_path = get_data("before_after_ff.h5")
    process(file, output_path)


if __name__ == '__main__':
    main()

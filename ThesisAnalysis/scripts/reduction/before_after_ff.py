from ThesisAnalysis import get_data, ThesisHDF5Writer, ThesisHDF5Reader
from ThesisAnalysis.files import Lab_TFPoly
import pandas as pd
from target_calib import CameraConfiguration
from CHECLabPy.core.io import DL1Reader
from tqdm import tqdm


class Processor:
    def __init__(self, file):
        self.file = file
        ff_path = get_data("ff_values.h5")
        illumination_path = file.illumination_profile_path

        with ThesisHDF5Reader(ff_path) as reader:
            df = reader.read("data")
            self.gamma_q = df['gamma_q'].values
            self.gamma_ff = df['gamma_ff'].values

        with ThesisHDF5Reader(illumination_path) as reader:
            self.correction = reader.read("correction")['correction']

        self.n_pixels = None
        self.n_samples = None
        self.cv = None

    def get_before_after(self, reader):
        pixel, charge = reader.select_columns(['pixel', 'charge'])
        df = pd.DataFrame(dict(
            pixel=pixel,
            charge=charge
        ))
        dead = self.file.dead
        df_mean = df.groupby('pixel').mean()
        pixel = df_mean.index.values
        charge = df_mean['charge'].values
        self.n_pixels = reader.n_pixels
        self.n_samples = reader.n_samples
        self.cv = reader.metadata['camera_version']

        before = charge / self.gamma_q
        after = charge * self.gamma_ff / self.gamma_q
        after_ip = after / self.correction

        df = pd.DataFrame(dict(
            pixel=pixel,
            before=before,
            after=after,
            after_ip=after_ip
        ))
        df = df.loc[~df['pixel'].isin(dead)]

        return df

    def process(self, illumination, output_path):
        path, exp, experr = self.file.get_run_with_illumination(illumination)
        with DL1Reader(path) as r:
            df = self.get_before_after(r)

        cfg = CameraConfiguration(self.cv)
        reference_pulse_path = cfg.GetReferencePulsePath()

        with ThesisHDF5Writer(output_path) as writer:
            writer.write(data=df)
            writer.write_metadata(
                expected=exp,
                expected_err=experr,
                n_pixels=self.n_pixels,
                n_samples=self.n_samples,
                reference_pulse_path=reference_pulse_path
            )

    def process_multi(self, output_path):
        df_runs = self.file.get_dataframe()
        n_runs = df_runs.index.size
        df_list = []
        desc0 = "Looping over files"
        it = enumerate(df_runs.iterrows())
        for i, (_, row) in tqdm(it, total=n_runs, desc=desc0):
            reader = row['reader']
            expected = row['expected']
            df = self.get_before_after(reader)
            df['expected'] = expected
            df_list.append(df)
            reader.store.close()
        df = pd.concat(df_list)

        with ThesisHDF5Writer(output_path) as writer:
            writer.write(data=df)
            writer.write_metadata(
                n_pixels=self.n_pixels,
                n_samples=self.n_samples,
            )


def main():
    processor = Processor(Lab_TFPoly())

    illumination = 50
    output_path = get_data("before_after_ff_50pe.h5")
    processor.process(illumination, output_path)

    illumination = 25
    output_path = get_data("before_after_ff_25pe.h5")
    processor.process(illumination, output_path)

    file = Lab_TFPoly()
    illumination = 100
    output_path = get_data("before_after_ff_100pe.h5")
    processor.process(illumination, output_path)

    output_path = get_data("before_after_ff_all.h5")
    processor.process_multi(output_path)


if __name__ == '__main__':
    main()

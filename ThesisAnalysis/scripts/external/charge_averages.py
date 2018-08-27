from ThesisAnalysis import ThesisHDF5Writer
from ThesisAnalysis.files import all_files
import pandas as pd
import os
from tqdm import tqdm
from CHECLabPy.utils.files import open_runlist_dl1
from CHECLabPy.utils.resolutions import ChargeStatistics


def process(file):
    runlist_path = file.runlist_path

    df_runs = open_runlist_dl1(runlist_path)
    df_runs['transmission'] = 1/df_runs['fw_atten']
    n_runs = df_runs.index.size
    mapping = df_runs.iloc[0]['reader'].mapping
    n_pixels = df_runs.iloc[0]['reader'].n_pixels

    cs = ChargeStatistics()

    desc0 = "Looping over files"
    it = enumerate(df_runs.iterrows())
    for i, (_, row) in tqdm(it, total=n_runs, desc=desc0):
        reader = row['reader']
        transmission = row['transmission']
        df = reader.get_first_n_events(1000)
        pixel = df['pixel'].values
        measured = df['charge'].values
        cs.add(pixel, transmission, measured)
        reader.store.close()
    df_pixel, df_camera = cs.finish()

    df = df_pixel[["pixel", "amplitude", "mean", "std"]].copy()
    df = df.rename(columns={"amplitude": "transmission"})
    df_runs2 = df_runs[['transmission', 'pe_expected', 'fw_pos']].copy()
    df_runs2['run_number'] = df_runs2.index
    df = pd.merge(df, df_runs2, on='transmission')

    output_dir = os.path.dirname(runlist_path)
    output_path = os.path.join(output_dir, "charge_averages.h5")

    with ThesisHDF5Writer(output_path) as writer:
        writer.write(data=df)
        writer.write_mapping(mapping)
        writer.write_metadata(n_pixels=n_pixels)


def main():
    [process(f) for f in all_files]


if __name__ == '__main__':
    main()

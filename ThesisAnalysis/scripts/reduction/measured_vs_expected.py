from ThesisAnalysis import ThesisHDF5Writer, ThesisHDF5Reader, get_data
from ThesisAnalysis.files import Lab_TFPoly, CHECM
from tqdm import tqdm
from CHECLabPy.utils.files import open_runlist_dl1
import pandas as pd


def process(file, output_path):

    runlist_path = file.runlist_path
    fw_path = file.fw_path
    ff_path = file.ff_path
    poi = file.poi

    df_runs = open_runlist_dl1(runlist_path)
    df_runs['transmission'] = 1/df_runs['fw_atten']
    n_runs = df_runs.index.size
    mapping = df_runs.iloc[0]['reader'].mapping
    n_pixels = df_runs.iloc[0]['reader'].n_pixels

    with ThesisHDF5Reader(fw_path) as reader:
        df = reader.read("data")
        fw_m = df['fw_m'].values
        fw_merr = df['fw_merr'].values

    with ThesisHDF5Reader(ff_path) as reader:
        df = reader.read("data")
        ff_m = df['ff_m'].values

    df_list = []

    desc0 = "Looping over files"
    it = enumerate(df_runs.iterrows())
    for i, (_, row) in tqdm(it, total=n_runs, desc=desc0):
        reader = row['reader']
        transmission = row['transmission']
        df = reader.get_first_n_events(1000)
        df = df.loc[df['pixel'] == poi]
        pixel = df['pixel'].values
        charge = df['charge'].values
        true = transmission * fw_m[pixel]
        true_err = transmission * fw_merr[pixel]
        measured = charge / ff_m[pixel]

        df_list.append(pd.DataFrame(dict(
            pixel=pixel,
            true=true,
            true_err=true_err,
            measured=measured,
        )))

        reader.store.close()

    df = pd.concat(df_list)

    with ThesisHDF5Writer(output_path) as writer:
        writer.write(
            data=df,
        )
        writer.write_mapping(mapping)
        writer.write_metadata(n_pixels=n_pixels)


def main():
    file = Lab_TFPoly()
    output_path = get_data("measured_vs_expected/measured_vs_expected_checs.h5")
    process(file, output_path)

    file = CHECM()
    output_path = get_data("measured_vs_expected/measured_vs_expected_checm.h5")
    process(file, output_path)


if __name__ == '__main__':
    main()

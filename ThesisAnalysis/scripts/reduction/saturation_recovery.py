from ThesisAnalysis import ThesisHDF5Reader, ThesisHDF5Writer, get_data
from ThesisAnalysis.files import Lab_TFPoly
from tqdm import tqdm
from CHECLabPy.utils.files import open_runlist_dl1
from CHECLabPy.utils.resolutions import ChargeStatistics


def process(file, output_path):
    runlist_path = file.runlist_path
    fw_path = file.fw_path

    df_runs = open_runlist_dl1(runlist_path)
    df_runs['transmission'] = 1/df_runs['fw_atten']
    n_runs = df_runs.index.size
    mapping = df_runs.iloc[0]['reader'].mapping
    n_pixels = df_runs.iloc[0]['reader'].n_pixels

    with ThesisHDF5Reader(fw_path) as reader:
        fw_m = reader.read("data")['fw_m'].values

    cs = ChargeStatistics()

    desc0 = "Looping over files"
    it = enumerate(df_runs.iterrows())
    for i, (_, row) in tqdm(it, total=n_runs, desc=desc0):
        reader = row['reader']
        transmission = row['transmission']
        df = reader.get_first_n_events(1000)
        pixel = df['pixel'].values
        expected_charge = transmission * fw_m[pixel]
        measured = df['saturation_coeff'].values
        cs.add(pixel, expected_charge, measured)
        reader.store.close()
    df_pixel, df_camera = cs.finish()

    with ThesisHDF5Writer(output_path) as writer:
        writer.write(data=df_pixel)
        writer.write_mapping(mapping)
        writer.write_metadata(n_pixels=n_pixels)


def main():
    file = Lab_TFPoly()
    output_path = get_data("saturation_recovery.h5")
    process(file, output_path)


if __name__ == '__main__':
    main()

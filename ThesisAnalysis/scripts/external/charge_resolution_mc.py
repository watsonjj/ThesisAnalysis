from ThesisAnalysis import ThesisHDF5Writer, ThesisHDF5Reader
from ThesisAnalysis.files import mc_files
from tqdm import tqdm
from CHECLabPy.utils.resolutions import ChargeStatistics, ChargeResolution


def process(file):

    reader_list = file.reader_list
    mc_calib_path = file.mc_calib_path
    output_path = file.charge_resolution_mc_path

    n_runs = len(reader_list)
    mapping = reader_list[0].mapping
    n_pixels = reader_list[0].n_pixels

    with ThesisHDF5Reader(mc_calib_path) as reader:
        df = reader.read("data")
        mc_m = df['mc_m'].values

    cr = ChargeResolution(mc_true=True)
    cs = ChargeStatistics()

    desc0 = "Looping over files"
    for reader in tqdm(reader_list, total=n_runs, desc=desc0):
        df = reader.get_first_n_events(1000)
        pixel = df['pixel'].values
        charge = df['charge'].values
        true = df['mc_true'].values
        measured = charge / mc_m[pixel]

        cr.add(pixel, true, measured)
        cs.add(pixel, true, measured)
        reader.store.close()
    df_cr_pixel, df_cr_camera = cr.finish()
    df_cs_pixel, df_cs_camera = cs.finish()

    with ThesisHDF5Writer(output_path) as writer:
        writer.write(
            charge_resolution_pixel=df_cr_pixel,
            charge_resolution_camera=df_cr_camera,
            charge_statistics_pixel=df_cs_pixel,
            charge_statistics_camera=df_cs_camera,
        )
        writer.write_mapping(mapping)
        writer.write_metadata(n_pixels=n_pixels)


def main():
    [process(f) for f in mc_files]


if __name__ == '__main__':
    main()

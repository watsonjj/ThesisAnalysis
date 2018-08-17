from ThesisAnalysis import ThesisHDF5Writer, ThesisHDF5Reader
import os
from tqdm import tqdm
from CHECLabPy.utils.files import open_runlist_dl1
from CHECLabPy.utils.resolutions import ChargeStatistics, ChargeResolution


def process(runlist_path, fw_path, ff_path):
    df_runs = open_runlist_dl1(runlist_path)
    df_runs['transmission'] = 1/df_runs['fw_atten']
    n_runs = df_runs.index.size
    mapping = df_runs.iloc[0]['reader'].mapping
    n_pixels = df_runs.iloc[0]['reader'].n_pixels

    with ThesisHDF5Reader(fw_path) as reader:
        df = reader.read("data")
        fw_m = df['fw_m'].values

    with ThesisHDF5Reader(ff_path) as reader:
        df = reader.read("data")
        ff_m = df['ff_m'].values
        ff_c = df['ff_c'].values

    cr = ChargeResolution()
    cs = ChargeStatistics()

    desc0 = "Looping over files"
    it = enumerate(df_runs.iterrows())
    for i, (_, row) in tqdm(it, total=n_runs, desc=desc0):
        reader = row['reader']
        transmission = row['transmission']
        df = reader.get_first_n_events(1000)
        pixel = df['pixel'].values
        charge = df['charge'].values

        true = transmission * fw_m[pixel]
        # measured = (charge - ff_c[pixel]) / ff_m[pixel]
        measured = charge / ff_m[pixel]

        cr.add(pixel, true, measured)
        cs.add(pixel, true, measured)
        reader.store.close()
    df_cr_pixel, df_cr_camera = cr.finish()
    df_cs_pixel, df_cs_camera = cs.finish()

    output_dir = os.path.dirname(runlist_path)
    output_path = os.path.join(output_dir, "charge_resolution.h5")

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
    fw_path = "/Users/Jason/Software/ThesisAnalysis/ThesisAnalysis/data/fw_calibration/mc_fw_calibration.h5"
    ff_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/5mhz/ff_coefficients.h5"
    paths = [
        "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/0mhz/runlist.txt",
        "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/5mhz/runlist.txt",
        "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/40mhz/runlist.txt",
        "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/125mhz/runlist.txt",
        "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/1200mhz/runlist.txt",
    ]
    # for p in paths:
    #     process(p, fw_path, ff_path)

    # fw_path = "/Users/Jason/Software/ThesisAnalysis/ThesisAnalysis/data/lab_tfnone_fw_calibration.h5"
    # ff_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_none/ff_coefficients.h5"
    # runlist_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_none/runlist.txt"
    # process(runlist_path, fw_path, ff_path)

    fw_path = "/Users/Jason/Software/ThesisAnalysis/ThesisAnalysis/data/lab_pchip_fw_calibration.h5"
    ff_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_pchip/ff_coefficients.h5"
    runlist_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_pchip/runlist.txt"
    process(runlist_path, fw_path, ff_path)

    # fw_path = "/Users/Jason/Software/ThesisAnalysis/ThesisAnalysis/data/lab_tfpoly_fw_calibration.h5"
    # ff_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_poly/ff_coefficients.h5"
    # runlist_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_poly/runlist.txt"
    # process(runlist_path, fw_path, ff_path)
    #
    fw_path = "/Users/Jason/Software/ThesisAnalysis/ThesisAnalysis/data/lab_tfwithped_fw_calibration.h5"
    ff_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_withped/ff_coefficients.h5"
    runlist_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_withped/runlist.txt"
    process(runlist_path, fw_path, ff_path)


if __name__ == '__main__':
    main()

from ThesisAnalysis import get_data, ThesisHDF5Writer, ThesisHDF5Reader
import numpy as np
import pandas as pd
import re
from CHECLabPy.utils.files import open_runlist_dl1


def process(runlist_path, spe_path, illumination_path, output_path):
    df_runs = open_runlist_dl1(runlist_path, False)
    df_runs['transmission'] = 1/df_runs['fw_atten']

    store_spe = pd.HDFStore(spe_path)
    df_spe = store_spe['coeff_pixel']

    meta_spe = store_spe.get_storer('metadata').attrs.metadata
    n_spe_illuminations = meta_spe['n_illuminations']
    spe_files = meta_spe['files']
    n_pixels = meta_spe['n_pixels']

    spe_transmission = []
    pattern = '(.+?)/Run(.+?)_dl1.h5'
    for path in spe_files:
        try:
            reg_exp = re.search(pattern, path)
            if reg_exp:
                run = int(reg_exp.group(2))
                spe_transmission.append(df_runs.loc[run]['transmission'])
        except AttributeError:
            print("Problem with Regular Expression, "
                  "{} does not match patten {}".format(path, pattern))

    pix_lambda = np.zeros((n_spe_illuminations, n_pixels))
    for ill in range(n_spe_illuminations):
        key = "lambda_" + str(ill)
        lambda_ = df_spe[['pixel', key]].sort_values('pixel')[key].values
        pix_lambda[ill] = lambda_

    with ThesisHDF5Reader(illumination_path) as reader:
        correction = reader.read("correction")['correction']
        mapping = reader.read_mapping()

    df_list = []
    for i in range(n_spe_illuminations):
        df_list.append(pd.DataFrame(dict(
            pixel=np.arange(n_pixels),
            correction=correction,
            transmission=spe_transmission[i],
            lambda_=pix_lambda[i]
        )))
    df_data = pd.concat(df_list)

    with ThesisHDF5Writer(output_path) as writer:
        writer.write(data=df_data)
        writer.write_mapping(mapping)
        writer.write_metadata(n_pixels=n_pixels)


def main():
    runlist_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/5mhz/runlist.txt"
    spe_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/5mhz/spe.h5"
    illumination_path = get_data("mc_illumination_profile_correction.h5")
    output_path = get_data("fw_calibration/mc_data.h5")
    process(runlist_path, spe_path, illumination_path, output_path)

    runlist_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/0mhz/runlist.txt"
    spe_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/0mhz/spe.h5"
    illumination_path = get_data("mc_illumination_profile_correction.h5")
    output_path = get_data("fw_calibration/mc_0mhz_data.h5")
    process(runlist_path, spe_path, illumination_path, output_path)

    runlist_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_pchip/runlist.txt"
    spe_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_pchip/spe.h5"
    illumination_path = get_data("mc_illumination_profile_correction.h5")  # TODO: get lab_illumination_profile_correction.h5
    output_path = get_data("fw_calibration/lab_tfpchip_data.h5")
    process(runlist_path, spe_path, illumination_path, output_path)

    runlist_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_none/runlist.txt"
    spe_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_none/spe.h5"
    illumination_path = get_data("mc_illumination_profile_correction.h5")  # TODO: get lab_illumination_profile_correction.h5
    output_path = get_data("fw_calibration/lab_tfnone_data.h5")
    process(runlist_path, spe_path, illumination_path, output_path)

    runlist_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_poly/runlist.txt"
    spe_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_poly/spe.h5"
    illumination_path = get_data("mc_illumination_profile_correction.h5")  # TODO: get lab_illumination_profile_correction.h5
    output_path = get_data("fw_calibration/lab_tfpoly_data.h5")
    process(runlist_path, spe_path, illumination_path, output_path)

    runlist_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_withped/runlist.txt"
    spe_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_withped/spe.h5"
    illumination_path = get_data("mc_illumination_profile_correction.h5")  # TODO: get lab_illumination_profile_correction.h5
    output_path = get_data("fw_calibration/lab_tfwithped_data.h5")
    process(runlist_path, spe_path, illumination_path, output_path)


if __name__ == '__main__':
    main()

from ThesisAnalysis import ThesisHDF5Writer
from ThesisAnalysis.files import mc_onsky_calib_files
import numpy as np
import pandas as pd
from CHECLabPy.utils.files import open_runlist_dl1
from CHECLabPy.core.io import DL1Reader
from numpy.polynomial.polynomial import polyfit
from glob import glob
from tqdm import tqdm


def process(file):

    input_paths = glob(file.glob_path)[:10]
    mc_calib_path = file.mc_calib_path
    readers = [DL1Reader(fp) for fp in input_paths]

    n_pixels = readers[0].n_pixels
    mapping = readers[0].mapping

    df_list = []
    for reader in tqdm(readers, total=len(readers), desc="Looping over files"):
        cols = ['pixel', 'charge', 'mc_true']
        pixel, charge, true = reader.select_columns(cols)
        df_list.append(pd.DataFrame(dict(
            pixel=pixel,
            charge=charge,
            true=true,
        )))
        reader.store.close()
    df = pd.concat(df_list, ignore_index=True)
    df_mean = df.groupby(['pixel', 'true']).mean().reset_index()
    df_std = df.groupby(['pixel', 'true']).std().reset_index()

    m_array = np.zeros(n_pixels)
    for p in range(n_pixels):
        df_p = df_mean.loc[df_mean['pixel'] == p]
        df_p_std = df_std.loc[df_std['pixel'] == p]
        x = df_p['true'].values
        y = df_p['charge'].values
        yerr = df_p_std['charge'].values
        yerr[np.isnan(yerr)] = 1000
        yerr[yerr == 0] = 1000
        c, m = polyfit(x, y, [1], w=y/yerr)
        m_array[p] = m

    df_calib = pd.DataFrame(dict(
        pixel=np.arange(n_pixels),
        mc_m=m_array,
    ))

    print("Average Gradient = {}".format(np.mean(m_array)))

    with ThesisHDF5Writer(mc_calib_path) as writer:
        writer.write(data=df_calib)
        writer.write_mapping(mapping)
        writer.write_metadata(n_pixels=n_pixels)


def main():
    [process(f) for f in mc_onsky_calib_files]


if __name__ == '__main__':
    main()

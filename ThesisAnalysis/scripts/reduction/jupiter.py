from ThesisAnalysis import ThesisHDF5Writer, get_data
import numpy as np
import pandas as pd
from tqdm import tqdm
from CHECLabPy.utils.mapping import get_clp_mapping_from_version
import warnings
from pandas.errors import PerformanceWarning
from IPython import embed


def main():
    file_df_list = [
        dict(type="on", deg=0, mirrors=2, fi=1,
             path="/Volumes/gct-jason/thesis_data/checm/jupiter/Run05451_rms.npy"),
        dict(type="on", deg=0, mirrors=2, fi=2,
             path="/Volumes/gct-jason/thesis_data/checm/jupiter/Run05452_rms.npy"),
        dict(type="off", deg=0, mirrors=2, fi=1,
             path="/Volumes/gct-jason/thesis_data/checm/jupiter/Run05453_rms.npy"),
        dict(type="off", deg=0, mirrors=2, fi=2,
             path="/Volumes/gct-jason/thesis_data/checm/jupiter/Run05454_rms.npy"),
        dict(type="on", deg=2, mirrors=2, fi=1,
             path="/Volumes/gct-jason/thesis_data/checm/jupiter/Run05455_rms.npy"),
        dict(type="on", deg=2, mirrors=2, fi=2,
             path="/Volumes/gct-jason/thesis_data/checm/jupiter/Run05456_rms.npy"),
        dict(type="on", deg=3.5, mirrors=2, fi=1,
             path="/Volumes/gct-jason/thesis_data/checm/jupiter/Run05457_rms.npy"),
        dict(type="on", deg=3.5, mirrors=2, fi=2,
             path="/Volumes/gct-jason/thesis_data/checm/jupiter/Run05458_rms.npy"),
        dict(type="on", deg=0, mirrors=1, fi=1,
             path="/Volumes/gct-jason/thesis_data/checm/jupiter/Run05459_rms.npy"),
        dict(type="on", deg=0, mirrors=1, fi=2,
             path="/Volumes/gct-jason/thesis_data/checm/jupiter/Run05460_rms.npy"),
        dict(type="on", deg=0, mirrors=1, fi=3,
             path="/Volumes/gct-jason/thesis_data/checm/jupiter/Run05461_rms.npy"),
        dict(type="on", deg=0, mirrors=1, fi=4,
             path="/Volumes/gct-jason/thesis_data/checm/jupiter/Run05462_rms.npy"),
        dict(type="off", deg=0, mirrors=1, fi=1,
             path="/Volumes/gct-jason/thesis_data/checm/jupiter/Run05463_rms.npy"),
        dict(type="off", deg=0, mirrors=1, fi=2,
             path="/Volumes/gct-jason/thesis_data/checm/jupiter/Run05464_rms.npy"),
        dict(type="off", deg=0, mirrors=1, fi=3,
             path="/Volumes/gct-jason/thesis_data/checm/jupiter/Run05465_rms.npy"),
        dict(type="off", deg=0, mirrors=1, fi=4,
             path="/Volumes/gct-jason/thesis_data/checm/jupiter/Run05466_rms.npy"),
        dict(type="on", deg=2, mirrors=1, fi=1,
             path="/Volumes/gct-jason/thesis_data/checm/jupiter/Run05471_rms.npy"),
        dict(type="on", deg=2, mirrors=1, fi=2,
             path="/Volumes/gct-jason/thesis_data/checm/jupiter/Run05472_rms.npy"),
        dict(type="on", deg=2, mirrors=1, fi=3,
             path="/Volumes/gct-jason/thesis_data/checm/jupiter/Run05473_rms.npy"),
        dict(type="on", deg=2, mirrors=1, fi=4,
             path="/Volumes/gct-jason/thesis_data/checm/jupiter/Run05474_rms.npy")
    ]
    df = pd.DataFrame(file_df_list)

    def consolidate_runs(row, pbar):
        array = np.load(row['path'])
        row['sum'] = np.sum(array, axis=0)
        row['n'] = array.shape[0]
        pbar.update(1)
        return row

    def get_mode_average(x):
        return np.sum(x['sum']) / np.sum(x['n'])

    n_files = len(df.index)
    desc = "Opening numpy files"
    with tqdm(total=n_files, desc=desc) as pbar:
        df = df.apply(consolidate_runs, pbar=pbar, axis=1)

    df = df.groupby(['mirrors', 'type', 'deg']).apply(get_mode_average)
    excess = df[:, 'on', :] - df[:, 'off', 0.0]

    mapping = get_clp_mapping_from_version("1.0.0")
    plate_scale = 40.344e-3

    output_path = get_data("jupiter.h5")
    with ThesisHDF5Writer(output_path) as writer:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', PerformanceWarning)
            writer.write(data=excess)
        writer.write_mapping(mapping)
        writer.write_metadata(
            plate_scale=plate_scale,
        )


if __name__ == '__main__':
    main()
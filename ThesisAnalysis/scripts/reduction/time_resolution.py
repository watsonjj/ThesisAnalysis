from ThesisAnalysis import ThesisHDF5Writer, get_data, ThesisHDF5Reader
from ThesisAnalysis.files import Lab_TFPoly, MCLab_Opct40_Window_5MHz, CHECM, MCLab_Opct40_Window_125MHz
import numpy as np
import pandas as pd
from tqdm import tqdm, trange
from IPython import embed


class Statistics:
    def __init__(self):
        self.n = 0
        self.sum = 0
        self.sum2 = 0

        self.mean = 0
        self.M2 = 0


        self._df_list = []
        self._df = pd.DataFrame()
        self._n_bytes = 0

    def add(self, t_diff):
        self.n += t_diff.size
        self.sum += np.sum(t_diff)
        self.sum2 += np.sum(t_diff**2)

    def finish(self):
        mean = self.sum / self.n
        std = np.sqrt((self.sum2 - self.sum**2/self.n) / (self.n - 1))
        return mean, std

    # def add(self, t_diff):
    #     for t in t_diff:
    #         self.n = self.n + 1
    #         delta = t - self.mean
    #         self.mean = self.mean + delta / self.n
    #         delta2 = t - self.mean
    #         self.M2 = self.M2 + delta * delta2
    #
    #     # return (count, mean, M2)
    #
    # def finish(self):
    #     mean = self.mean
    #     std = np.sqrt(self.M2 / self.n)
    #     sampleStd = np.sqrt(self.M2 / self.n - 1)
    #     return mean, std



def process(file, time_corr_path, output_path):
    df_runs = file.get_dataframe(open_readers=True)
    # df_runs = df_runs.iloc[50:]
    n_runs = df_runs.index.size
    dead = file.dead
    fw_path = file.fw_path

    with ThesisHDF5Reader(fw_path) as reader:
        fw_m = reader.read_metadata()['fw_m_camera']
        fw_merr = reader.read_metadata()['fw_merr_camera']

    with ThesisHDF5Reader(time_corr_path) as reader:
        t_corr = reader.read("data")['t_corr'].values
        n_pixels = reader.read_metadata()['n_pixels']

    d_list = []
    n_pixelsd = n_pixels - len(dead)
    mask = np.zeros((n_pixelsd, n_pixelsd), dtype=np.bool)
    np.fill_diagonal(mask, 1)
    mask[np.tril_indices(mask.shape[0], -1)] = 1

    desc0 = "Looping over files"
    it = enumerate(df_runs.iterrows())
    for i, (_, row) in tqdm(it, total=n_runs, desc=desc0):
        stats = Statistics()
        reader = row['reader']
        transmission = row['transmission']

        pixel, iev, t_pulse = reader.select_columns(['pixel', 'iev', 't_pulse'], stop=100*n_pixels)
        df = pd.DataFrame(dict(
            pixel=pixel,
            iev=iev,
            t_pulse=t_pulse,
        ))
        df = df.loc[~df['pixel'].isin(dead)]
        df['t_pulse'] -= t_corr[df['pixel'].values]
        n_events = df.index.size // n_pixelsd

        # t_pulse = df['t_pulse'].values
        # t_pulse = t_pulse.reshape((n_events, n_pixelsd))
        # t_diff = t_pulse[:, :, None] - t_pulse[:, None, :]
        # t_diff = np.ma.masked_array(t_diff, mask=np.tile(mask, (n_events, 1, 1))).compressed()
        # mean = np.nanmean(t_diff)
        # std = np.nanstd(t_diff, ddof=1)

        for iev in trange(n_events):
            df_i = df.iloc[iev*n_pixelsd:(iev+1)*n_pixelsd]
            t_pulse = df_i['t_pulse'].values
            t_diff = t_pulse[:, None] - t_pulse[None, :]
            t_diff = np.ma.masked_array(t_diff, mask=mask)
            t_diff_c = t_diff.compressed()
            t_diff_c = t_diff_c[~np.isnan(t_diff_c)]
            stats.add(t_diff_c)
        mean, std = stats.finish()
        d_list.append(dict(
            expected=transmission*fw_m,
            expected_err=transmission*fw_merr,
            mean=mean,
            std=std,
        ))
        reader.store.close()

    df = pd.DataFrame(d_list)

    with ThesisHDF5Writer(output_path) as writer:
        writer.write(data=df)


def main():
    # file = Lab_TFPoly()
    # time_corr_path = get_data("time_corrections/time_corrections_lab.h5")
    # output_path = get_data("time_resolution/lab.h5")
    # process(file, time_corr_path, output_path)

    file = MCLab_Opct40_Window_5MHz()
    time_corr_path = get_data("time_corrections/time_corrections_mc.h5")
    output_path = get_data("time_resolution/mc.h5")
    process(file, time_corr_path, output_path)

    file = MCLab_Opct40_Window_125MHz()
    time_corr_path = get_data("time_corrections/time_corrections_mc.h5")
    output_path = get_data("time_resolution/mc125.h5")
    process(file, time_corr_path, output_path)

    # file = CHECM()
    # time_corr_path = get_data("time_corrections/time_corrections_checm.h5")
    # output_path = get_data("time_resolution/checm.h5")
    # process(file, time_corr_path, output_path)


if __name__ == '__main__':
    main()
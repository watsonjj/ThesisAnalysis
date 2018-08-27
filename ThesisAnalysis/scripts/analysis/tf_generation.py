from ThesisAnalysis.plotting.setup import ThesisPlotter
from ThesisAnalysis import get_data, get_plot, ThesisHDF5Reader
from matplotlib.ticker import MultipleLocator
import numpy as np
from IPython import embed


class Waveform(ThesisPlotter):
    def plot(self, df, ifile):
        df_event = df.loc[df['ifile'] == ifile]
        x = df_event['isam']
        y = df_event['wf']
        self.ax.plot(x, y, 'black', lw=0.1)

        self.ax.set_xlabel("Time (ns)")
        self.ax.set_ylabel("Amplitude (ADC)")

        self.ax.xaxis.set_major_locator(MultipleLocator(16))


def process(input_path, output_path):
    with ThesisHDF5Reader(input_path) as reader:
        df = reader.read("data")
        n_files = reader.read_metadata()['n_files']

    n_samples = df['isam'].max() + 1
    nan = df.groupby('ifile').count()['wf'] < n_samples
    nan_where = np.where(~nan)[0]
    df = df.loc[df['ifile'].isin(nan_where)]

    p_wf = Waveform(sidebyside=True)

    for ifile in range(n_files):

        # df_event = df.loc[df['ifile'] == ifile]
        # y = df_event['wf'].values
        # file = df_event['file'].values[0]
        # print(file, y.std())

        p_wf.plot(df, ifile)

    # embed()

    p_wf.save(output_path)


def main():
    input_path = get_data("tf/t5_input.h5")
    output_path = get_plot("tf/generation_t5.pdf")
    process(input_path, output_path)

    input_path = get_data("tf/tc_input.h5")
    output_path = get_plot("tf/generation_tc.pdf")
    process(input_path, output_path)


if __name__ == '__main__':
    main()

from ThesisAnalysis.plotting.setup import ThesisPlotter
from ThesisAnalysis import get_data, get_plot, ThesisHDF5Reader
import os
import numpy as np
from matplotlib.ticker import MultipleLocator
from target_calib import CalculateRowColumnBlockPhase, GetCellIDTCArray


def setup_cells(df, camera):
    fci = df['fci'].values.astype(np.uint16)
    frow, fcolumn, fblockphase = CalculateRowColumnBlockPhase(fci)
    fblock = fcolumn * 8 + frow
    df['fblock'] = fblock
    df['fblockphase'] = fblockphase
    df['fbpisam'] = df['fblockphase'] + df['isam']

    if "checs" in camera:
        cell = GetCellIDTCArray(fci, df['isam'].values)
    else:
        cell = (fci + df['isam'].values) % 2**14
    row, column, blockphase = CalculateRowColumnBlockPhase(cell)
    block = column * 8 + row
    df['cell'] = cell
    df['block'] = block
    df['blockphase'] = blockphase

    df['iblock'] = (df['isam'] + df['fblockphase']) // 32

    return df


class Hist(ThesisPlotter):
    def __init__(self):
        super().__init__()

        self.ax2 = self.ax.twiny()

    def plot(self, r0, r1):
        c1 = next(self.ax._get_lines.prop_cycler)['color']
        c2 = next(self.ax._get_lines.prop_cycler)['color']

        label = "Mean = {:.3f}, Stddev = {:.3f}, N = {:.3e}"
        label_r0 = label.format(r0.mean(), r0.std(), r0.size)
        label_r1 = label.format(r1.mean(), r1.std(), r1.size)

        self.ax2.hist(r0, bins=40, color=c2, alpha=0.5, label=label_r0)
        self.ax.hist(r1, bins=40, color=c1, alpha=0.5, label=label_r1)

        self.ax.set_ylabel('Counts')
        self.ax2.set_xlabel('Raw Samples (ADC)')
        self.ax2.tick_params('x', which='both', colors=c2)
        self.ax.set_xlabel('Pedestal-Subtracted Samples (ADC)')
        self.ax.tick_params('x', which='both', colors=c1)

        lines, labels = self.ax.get_legend_handles_labels()
        lines2, labels2 = self.ax2.get_legend_handles_labels()
        self.ax.legend(lines + lines2, labels + labels2, loc=2)


class HistChunk(ThesisPlotter):
    def plot(self, r1):
        size = r1.size
        chunksize = size // 5

        label = "Mean = {:.3f}, Stddev = {:.3f}, N = {:.3e}"

        for i in range(5):
            s = r1[i * chunksize:(i+1) * chunksize]
            label_s = label.format(s.mean(), s.std(), s.size)
            self.ax.hist(s, bins=40, alpha=0.5, label=label_s)

        self.ax.set_xlabel('Pedestal-Subtracted Samples (ADC)')
        self.ax.set_ylabel('Counts')
        self.add_legend('best')


class LookupTable(ThesisPlotter):
    def plot(self, data, data_title=""):
        pixel_hits_0 = np.ma.masked_where(data == 0, data)

        im = self.ax.pcolor(pixel_hits_0, cmap="viridis",
                            edgecolors='white', linewidths=0.1)
        cbar = self.fig.colorbar(im)
        self.ax.patch.set(hatch='xx')
        self.ax.set_xlabel("Blockphase + Waveform position")
        self.ax.set_ylabel("Block")
        cbar.set_label(data_title)

        # self.ax.set_ylim(110, 120)


class Waveform(ThesisPlotter):
    def plot(self, df, event):
        df_event = df.loc[df['iev'] == event]
        x = df_event['isam']
        y = df_event['r0']
        self.ax.plot(x, y, color='black')

        self.ax.set_xlabel("Time (ns)")
        self.ax.set_ylabel("Amplitude (Raw ADC)")

        self.ax.xaxis.set_major_locator(MultipleLocator(16))



class CellWaveform(ThesisPlotter):
    def plot(self, df, cell):
        df_mean = df.loc[df['cell'] == cell].groupby('isam').mean()
        df_std = df.loc[df['cell'] == cell].groupby('isam').std()

        x = df_mean.index
        y = df_mean['r0']
        yerr = df_std['r0']

        block_edges_flag = np.where(np.diff(df_mean['iblock']))[0]
        block_edges = df_mean.index[block_edges_flag]
        block_edges = list(block_edges) + [x.min(), x.max()]

        [self.ax.axvline(l, ls='--', color='gray', alpha=0.7)
         for l in block_edges]
        self.ax.errorbar(x, y, yerr=yerr, color='black')

        self.ax.set_xlabel("Position in waveform")
        self.ax.set_ylabel("Amplitude (Raw ADC)")
        # self.ax.set_title("Cell = {}".format(cell))

        self.ax.xaxis.set_major_locator(MultipleLocator(16))


class BlockPlotter(ThesisPlotter):
    def plot(self, df, block):
        df_block = df.loc[df['block'] == block]
        for iblock, group in df_block.groupby('iblock'):
            df_cell = group.groupby('cell').mean()
            value = df_cell['r0']
            self.ax.plot(value, label="{}".format(iblock))

        self.ax.set_xlabel("Cell")
        self.ax.set_ylabel("Amplitude (Raw ADC)")
        # self.ax.set_title("Block = {}".format(block))
        self.add_legend('best', title="Block Position in Waveform")


def process(camera, input_path):
    with ThesisHDF5Reader(input_path) as reader:
        df = reader.read("data")

    df = setup_cells(df, camera)

    r0 = df['r0'].values
    r1 = df['r1'].values

    output_dir = get_plot("pedestal/{}".format(camera))

    p_hist = Hist()
    p_hist.plot(r0, r1)
    p_hist.save(os.path.join(output_dir, "pedestal_hist.pdf"))

    p_histchunk = HistChunk()
    p_histchunk.plot(r1)
    p_histchunk.save(os.path.join(output_dir, "pedestal_histchunk.pdf"))

    d = df.groupby(['fblock', 'fbpisam']).mean()['r0'].unstack().values
    p_lookup = LookupTable(switch_backend=True)
    p_lookup.plot(d, "Pedestal Value")
    p_lookup.save(os.path.join(output_dir, "pedestal_lookup.pdf"))

    e = 10
    p_wf = Waveform(sidebyside=True)
    p_wf.plot(df, e)
    p_wf.save(os.path.join(output_dir, "rawwf_{}.pdf".format(e)))

    cells = [15, 26, 75, 76]
    for c in cells:
        p_cellwf = CellWaveform()
        p_cellwf.plot(df, c)
        p_cellwf.save(os.path.join(output_dir, "cellwf_{}.pdf".format(c)))

    b = 40
    p_block = BlockPlotter()
    p_block.plot(df, b)
    p_block.save(os.path.join(output_dir, "block_{}.pdf".format(b)))


def main():
    camera = "checs"
    input_path = get_data("pedestal/pedestal_checs.h5")
    process(camera, input_path)

    camera = "checs_mV"
    input_path = get_data("pedestal/pedestal_checs_mV.h5")
    process(camera, input_path)

    camera = "checs_pe"
    input_path = get_data("pedestal/pedestal_checs_pe.h5")
    process(camera, input_path)

    camera = "checm"
    input_path = get_data("pedestal/pedestal_checm.h5")
    process(camera, input_path)


if __name__ == '__main__':
    main()

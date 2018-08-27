from ThesisAnalysis.plotting.setup import ThesisPlotter
from ThesisAnalysis import get_data, get_plot, ThesisHDF5Reader
import numpy as np


class TFPlotter(ThesisPlotter):
    def plot(self, x, y):

        ymax = np.max(y, 0)
        ymin = np.min(y, 0)

        color = next(self.ax._get_lines.prop_cycler)['color']
        self.ax.fill_between(x, ymin, ymax,
                             facecolor='black', edgecolor='black',
                             label="Range Across Cells")
        self.ax.plot(x, y[0], color=color, lw=1,
                     label="Single Cell")

        self.ax.set_xlabel("Sample (ADC)")
        self.ax.set_ylabel("Calibrated Sample (mV)")
        self.add_legend(2)


def process(input_path, output_path):
    with ThesisHDF5Reader(input_path) as reader:
        x = reader.read("x")['x'].values
        y_flat = reader.read("y")['y'].values
        metadata = reader.read_metadata()
        n_cells = metadata['n_cells']
        n_pnts = metadata['n_pnts']

    y = y_flat.reshape((n_cells, n_pnts))

    p_tf = TFPlotter(sidebyside=True)
    p_tf.plot(x, y)
    p_tf.save(output_path)


def main():
    input_path = get_data("tf/t5_lookup.h5")
    output_path = get_plot("tf/lookup_t5.pdf")
    process(input_path, output_path)

    input_path = get_data("tf/tc_lookup.h5")
    output_path = get_plot("tf/lookup_tc.pdf")
    process(input_path, output_path)


if __name__ == '__main__':
    main()

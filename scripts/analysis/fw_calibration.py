from ThesisAnalysis import get_data, ThesisHDF5Reader, get_plot, \
    ThesisHDF5Writer
from ThesisAnalysis.plotting.setup import ThesisPlotter
import numpy as np
import pandas as pd
from numpy.polynomial.polynomial import polyfit
import seaborn as sns
import os


class LinePlotter(ThesisPlotter):
    def plot(self, m_avg, m_pix):
        x = np.linspace(0, 1, 100)
        y_avg = x * m_avg
        y_pix = x[:, None] * m_pix[None, :]

        imax = np.argmax(m_pix)
        imin = np.argmin(m_pix)

        color = next(self.ax._get_lines.prop_cycler)['color']
        self.ax.fill_between(x, y_pix[:, imin], y_pix[:, imax],
                             facecolor=color, edgecolor=color,
                             label="Individual Camera Pixel Range")
        self.ax.plot(x, y_avg, color='black',
                     label="Light-Profile-Corrected Camera Average")

        self.ax.set_xlabel("Filter Wheel Transmission")
        self.ax.set_ylabel("Expected Average Illumination (p.e.)")
        self.add_legend('best')


class HistPlotter(ThesisPlotter):
    def plot(self, m_corrected):
        rel_pde = m_corrected / m_corrected.mean()
        std = np.std(rel_pde)

        label = ("Standard Deviation: {:.3f}".format(std))

        sns.distplot(rel_pde, ax=self.ax, hist=True, kde=False,
                     kde_kws={'shade': True, 'linewidth': 3},
                     label=label, norm_hist=False)

        self.ax.set_xlabel("Relative Photon Detection "
                           "Efficiency Between Pixels")
        self.ax.set_ylabel("Count")
        self.add_legend('best')


def process(input_path, dead, output_ref):

    with ThesisHDF5Reader(input_path) as reader:
        df = reader.read("data")
        mapping = reader.read_mapping()
        metadata = reader.read_metadata()

    n_pixels = metadata['n_pixels']
    dead_mask = np.zeros(n_pixels, dtype=np.bool)
    dead_mask[dead] = True

    transmission = np.unique(df['transmission'].values)
    lambda_ = []
    corrections = []
    for i in range(len(transmission)):
        df_t = df.loc[df['transmission'] == transmission[i]]
        lambda_.append(df_t['lambda_'].values)
        corrections.append(df_t['correction'].values)
    correction = corrections[0]

    c, m = polyfit(transmission, lambda_, 1)

    m_corrected = m / correction
    m_avg = np.mean(m_corrected[~dead_mask])
    m_pix = m_avg * correction

    df_calib = pd.DataFrame(dict(
        pixel=np.arange(n_pixels),
        fw_m=m_pix
    ))
    df_calib = df_calib.sort_values('pixel')

    output_dir = get_plot("fw_calibration")

    path = get_data("fw_calibration/" + output_ref + "fw_calibration.h5")
    with ThesisHDF5Writer(path) as writer:
        writer.write(data=df_calib)
        writer.write_mapping(mapping)
        writer.write_metadata(n_pixels=n_pixels)

    p_line = LinePlotter()
    p_line.plot(m_avg, m_pix)
    p_line.save(os.path.join(output_dir, output_ref+"fw_calibration.pdf"))

    p_hist = HistPlotter()
    p_hist.plot(m_corrected)
    p_hist.save(os.path.join(output_dir, output_ref+"relative_pde.pdf"))


def main():
    input_path = get_data("fw_calibration/mc_data.h5")
    dead = []
    output_ref = "mc_"
    process(input_path, dead, output_ref)

    input_path = get_data("fw_calibration/mc_0mhz_data.h5")
    dead = []
    output_ref = "mc_0mhz_"
    process(input_path, dead, output_ref)

    input_path = get_data("fw_calibration/lab_tfpchip_data.h5")
    dead = [677, 293, 27, 1925]
    output_ref = "lab_tfpchip_"
    process(input_path, dead, output_ref)

    input_path = get_data("fw_calibration/lab_tfnone_data.h5")
    dead = [677, 293, 27, 1925]
    output_ref = "lab_tfnone_"
    process(input_path, dead, output_ref)

    input_path = get_data("fw_calibration/lab_tfpoly_data.h5")
    dead = [677, 293, 27, 1925]
    output_ref = "lab_tfpoly_"
    process(input_path, dead, output_ref)

    input_path = get_data("fw_calibration/lab_tfwithped_data.h5")
    dead = [677, 293, 27, 1925]
    output_ref = "lab_tfwithped_"
    process(input_path, dead, output_ref)


if __name__ == '__main__':
    main()

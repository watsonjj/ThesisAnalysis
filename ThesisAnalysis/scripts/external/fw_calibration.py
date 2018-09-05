from ThesisAnalysis.plotting.setup import ThesisPlotter
from ThesisAnalysis import ThesisHDF5Writer, ThesisHDF5Reader
from ThesisAnalysis.files import calib_files
import numpy as np
import pandas as pd
import re
from CHECLabPy.utils.files import open_runlist_dl1
from numpy.polynomial.polynomial import polyfit, polyval
import seaborn as sns
import os


class FitPlotter(ThesisPlotter):
    def plot(self, x, y, c, m):
        xf = np.linspace(x.min(), x.max(), 2)
        yf = polyval(xf, (c, m))

        color = self.ax._get_lines.get_next_color()
        self.ax.plot(x, y, 'x', color=color)
        self.ax.plot(xf, yf.T, color=color)

        self.ax.set_xlabel("Filter-Wheel Transmission")
        self.ax.set_ylabel("Lambda (p.e.)")


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
                             label="Range for True Pixel Positions")
        self.ax.plot(x, y_avg, color='black',
                     label="Pixel at Camera Centre")

        self.ax.set_xlabel("Filter-Wheel Transmission")
        self.ax.set_ylabel("Expected Charge (p.e.)")
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


def process(file):

    runlist_path = file.spe_runlist_path
    spe_path = file.spe_path
    illumination_path = file.illumination_profile_path
    dead = file.dead
    fw_path = file.fw_path
    output_dir = os.path.dirname(runlist_path)

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
    df = pd.concat(df_list)

    # Obtain calibration
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

    with ThesisHDF5Writer(fw_path) as writer:
        writer.write(data=df_calib)
        writer.write_mapping(mapping)
        writer.write_metadata(
            n_pixels=n_pixels,
            fw_m_camera=m_avg,
        )

    p_fit = FitPlotter()
    p_fit.plot(transmission, np.array(lambda_)[:, :3], c[:3], m[:3])
    p_fit.save(os.path.join(output_dir, "fw_calibration_fit.pdf"))

    p_line = LinePlotter()
    p_line.plot(m_avg, m_pix)
    p_line.save(os.path.join(output_dir, "fw_calibration.pdf"))

    p_hist = HistPlotter()
    p_hist.plot(m_corrected[~dead_mask])
    p_hist.save(os.path.join(output_dir, "relative_pde.pdf"))


def main():
    [process(f) for f in calib_files]


if __name__ == '__main__':
    main()

from ThesisAnalysis.plotting.setup import ThesisPlotter
from ThesisAnalysis import ThesisHDF5Reader, get_plot
from ThesisAnalysis.plotting.camera import CameraImage
import numpy as np
from IPython import embed


class HillasPlotter(ThesisPlotter):
    def __init__(self, xlabel, ylabel, **kwargs):
        super().__init__(**kwargs)
        self.xlabel = xlabel
        self.ylabel = ylabel

    def plot(self, x, y, label="", fmt='o', **kwargs):
        self.ax.plot(x, y, fmt, label=label, **kwargs)

    def plot_interesting(self, x, y, label="", fmt='o', **kwargs):
        self.ax.plot(x, y, fmt, label=label, **kwargs)
        # self.ax.text(x, y, label, fontsize=4)

    def finish(self):
        self.ax.set_xlabel(self.xlabel)
        self.ax.set_ylabel(self.ylabel)

        self.add_legend("best")


class HillasHist(ThesisPlotter):
    def plot(self, gamma, proton, xlabel):
        self.ax.hist(gamma, bins='auto', label="Gamma", histtype='step')
        self.ax.hist(proton, bins='auto', label="Proton", histtype='step')

        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel("Counts")

        self.add_legend("best")

def main():

    input_path = "/Volumes/gct-jason/thesis_data/checs/mc/onsky/proton/v2/checs_gamma_dl1b.h5"
    with ThesisHDF5Reader(input_path) as reader:
        df_gamma = reader.read("data")

    input_path = "/Volumes/gct-jason/thesis_data/checs/mc/onsky/proton/v2/checs_proton_dl1b.h5"
    with ThesisHDF5Reader(input_path) as reader:
        df_proton = reader.read("data")

    p_hist = HillasHist(sidebyside=True)
    p_hist.plot(df_gamma['width'].values, df_proton['width'].values, r"Width ($\degree$)")
    p_hist.save(get_plot("hillas/checs/width.pdf"))

    p_hist = HillasHist(sidebyside=True)
    p_hist.plot(df_gamma['length'].values, df_proton['length'].values, r"Length ($\degree$)")
    p_hist.save(get_plot("hillas/checs/length.pdf"))

    p_hist = HillasHist(sidebyside=True)
    p_hist.plot(df_gamma['r'].values, df_proton['length'].values, "r")
    p_hist.save(get_plot("hillas/checs/r.pdf"))

    p_hist = HillasHist(sidebyside=True)
    p_hist.plot(df_gamma['phi'].values, df_proton['phi'].values, "phi")
    p_hist.save(get_plot("hillas/checs/phi.pdf"))

    p_hist = HillasHist(sidebyside=True)
    p_hist.plot(df_gamma['psi'].values, df_proton['phi'].values, "psi")
    p_hist.save(get_plot("hillas/checs/psi.pdf"))

    p_hist = HillasHist(sidebyside=True)
    p_hist.plot(df_gamma['miss'].values, df_proton['phi'].values, "miss")
    p_hist.save(get_plot("hillas/checs/miss.pdf"))

    p_hist = HillasHist(sidebyside=True)
    p_hist.plot(df_gamma['skewness'].values, df_proton['skewness'].values, "skewness")
    p_hist.save(get_plot("hillas/checs/skewness.pdf"))

    p_hist = HillasHist(sidebyside=True)
    p_hist.plot(df_gamma['kurtosis'].values, df_proton['kurtosis'].values, "kurtosis")
    p_hist.save(get_plot("hillas/checs/kurtosis.pdf"))

    # def add(iev, label, image_path, time_path, color=None, add=True):
    #     df_im = df_cam.loc[df_cam['iev'] == iev]
    #     image = df_im['image'].values[0]
    #     peakpos = df_im['peakpos'].values[0]
    #     tailcuts = df_im['tailcuts'].values[0]
    #     tailcuts_w = np.where(tailcuts)
    #     peakpos = np.ma.masked_array(peakpos, mask=~tailcuts)
    #     p_ci = CameraImage.from_mapping(mapping)
    #     p_ci.image = image
    #     p_ci.add_colorbar("Charge (p.e.)")
    #     p_ci.highlight_pixels(tailcuts_w, 'white', 0.5, 1)
    #     p_ci.save(image_path)
    #     p_ci = CameraImage.from_mapping(mapping)
    #     p_ci.image = peakpos
    #     p_ci.add_colorbar("Signal Time (ns)")
    #     p_ci.highlight_pixels(np.arange(2048), 'black', 0.2, 1)
    #     p_ci.save(time_path)
    #     width = df_im['width'].values[0]
    #     length = df_im['length'].values[0]
    #     if add:
    #         p_width_length.plot_interesting(width, length, fmt='x', mew=0.7,
    #                                         ms=5, label=label, color=color)
    #
    # add(
    #     46,
    #     r"Direct CR Entry\&Exit",
    #     get_plot("hillas/checm/cr_ee.pdf"),
    #     get_plot("hillas/checm/cr_ee_time.pdf")
    # )
    # add(
    #     117,
    #     "Bright Shower",
    #     get_plot("hillas/checm/bright.pdf"),
    #     get_plot("hillas/checm/bright_time.pdf"),
    #     add=False
    # )
    # add(
    #     124,
    #     "Direct CR",
    #     get_plot("hillas/checm/cr.pdf"),
    #     get_plot("hillas/checm/cr_time.pdf")
    # )
    # add(
    #     136,
    #     "Typical Shower",
    #     get_plot("hillas/checm/typical.pdf"),
    #     get_plot("hillas/checm/typical_time.pdf"),
    #     color='black'
    # )
    # add(
    #     9,
    #     "Bright Shower",
    #     get_plot("hillas/checm/bright2.pdf"),
    #     get_plot("hillas/checm/bright2_time.pdf")
    # )

    # p_width_length.save(get_plot("hillas/checs/width_length.pdf"))


if __name__ == '__main__':
    main()
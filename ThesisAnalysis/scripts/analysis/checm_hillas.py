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


def main():
    p_width_length = HillasPlotter(r"Width ($\degree$)", r"Length ($\degree$)")

    input_path = "/Volumes/gct-jason/thesis_data/checm/cherenkov/Run05477_dl1b.h5"
    with ThesisHDF5Reader(input_path) as reader:
        df_cam = reader.read("data")
        mapping = reader.read_mapping()
        width = df_cam['width'].values
        length = df_cam['length'].values
        p_width_length.plot(width, length, fmt='o', ms=0.7, label='Real', zorder=2)

    input_path = "/Volumes/gct-jason/thesis_data/checm/cherenkov/meudon_cr/proton_dl1b.h5"
    with ThesisHDF5Reader(input_path) as reader:
        df_sim = reader.read("data")
        width = df_sim['width'].values
        length = df_sim['length'].values
        p_width_length.plot(width, length, fmt='*', ms=0.7, label='Simulation', zorder=1)

    input_path = "/Volumes/gct-jason/thesis_data/checm/cherenkov/meudon_cr/proton_heidefix_dl1b.h5"
    with ThesisHDF5Reader(input_path) as reader:
        df_simcorr = reader.read("data")
        width = df_simcorr['width'].values
        length = df_simcorr['length'].values
        p_width_length.plot(width, length, fmt='v', ms=0.5, label='Simulation (Out-of-Focus)', zorder=1)

    def add(iev, label, image_path, time_path, color=None, add=True):
        df_im = df_cam.loc[df_cam['iev'] == iev]
        image = df_im['image'].values[0]
        peakpos = df_im['peakpos'].values[0]
        tailcuts = df_im['tailcuts'].values[0]
        tailcuts_w = np.where(tailcuts)
        peakpos = np.ma.masked_array(peakpos, mask=~tailcuts)
        p_ci = CameraImage.from_mapping(mapping)
        p_ci.image = image
        p_ci.add_colorbar("Charge (p.e.)")
        p_ci.highlight_pixels(tailcuts_w, 'white', 0.2, 1)
        # p_ci.save(image_path)
        p_ci = CameraImage.from_mapping(mapping)
        p_ci.image = peakpos
        p_ci.add_colorbar("Signal Time (ns)")
        p_ci.highlight_pixels(np.arange(2048), 'black', 0.2, 1)
        # p_ci.save(time_path)
        width = df_im['width'].values[0]
        length = df_im['length'].values[0]
        if add:
            p_width_length.plot_interesting(width, length, fmt='x', mew=0.7,
                                            ms=5, label=label, color=color)

    add(
        136,
        "Typical Shower",
        get_plot("hillas/checm/typical.pdf"),
        get_plot("hillas/checm/typical_time.pdf"),
        color='black'
    )
    add(
        117,
        "Bright Shower",
        get_plot("hillas/checm/bright.pdf"),
        get_plot("hillas/checm/bright_time.pdf"),
        add=False
    )
    add(
        9,
        "Bright Shower",
        get_plot("hillas/checm/bright2.pdf"),
        get_plot("hillas/checm/bright2_time.pdf")
    )
    add(
        124,
        "Direct CR",
        get_plot("hillas/checm/cr.pdf"),
        get_plot("hillas/checm/cr_time.pdf")
    )
    add(
        46,
        r"Direct CR Entry\&Exit",
        get_plot("hillas/checm/cr_ee.pdf"),
        get_plot("hillas/checm/cr_ee_time.pdf")
    )

    p_width_length.save(get_plot("hillas/checm/width_length.pdf"))


if __name__ == '__main__':
    main()
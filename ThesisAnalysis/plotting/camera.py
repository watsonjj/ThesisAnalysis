from ThesisAnalysis.plotting.setup import ThesisPlotter
import numpy as np
import matplotlib as mpl
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle
from CHECLabPy.utils.mapping import get_clp_mapping_from_tc_mapping


class CameraImage(ThesisPlotter):
    def __init__(self, xpix, ypix, size, **kwargs):
        """
        Create a camera-image plot

        Parameters
        ----------
        xpix : ndarray
            The X positions of the pixels/superpixels/TMs
        ypix : ndarray
            The Y positions of the pixels/superpixels/TMs
        size : float
            The size of the pixels/superpixels/TMs
        kwargs
            Arguments passed to `CHECLabPy.plottong.setup.Plotter`
        """
        super().__init__(**kwargs)

        rc = {
            "xtick.direction": 'out',
            "ytick.direction": 'out',
        }
        mpl.rcParams.update(rc)

        self._image = None
        self._mapping = None
        self.colorbar = None
        self.autoscale = True

        self.xpix = xpix
        self.ypix = ypix

        assert self.xpix.size == self.ypix.size
        self.n_pixels = self.xpix.size

        patches = []
        for xx, yy in zip(self.xpix, self.ypix):
            rr = size + 0.0001  # extra size to pixels to avoid aliasing
            poly = Rectangle(
                (xx - rr / 2., yy - rr / 2.),
                width=rr,
                height=rr,
                fill=True,
            )
            patches.append(poly)

        self.pixels = PatchCollection(patches, linewidth=0)
        self.ax.add_collection(self.pixels)
        self.pixels.set_array(np.zeros(self.n_pixels))

        self.ax.set_aspect('equal', 'datalim')
        self.ax.set_xlabel("X position (m)")
        self.ax.set_ylabel("Y position (m)")
        self.ax.autoscale_view()
        self.ax.axis('off')

    @staticmethod
    def figsize(scale=0.9):
        fig_width_pt = 469.755  # Get this from LaTeX using \the\textwidth
        inches_per_pt = 1.0 / 72.27  # Convert pt to inch
        golden_mean = (np.sqrt(5.0) - 1.0) / 2.0  # Aesthetic ratio
        fig_width = fig_width_pt * inches_per_pt * scale  # width in inches
        fig_height = fig_width * 0.8# * golden_mean * 1  # height in inches
        fig_size = [fig_width, fig_height]
        return fig_size

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, val):
        assert val.size == self.n_pixels

        self.pixels.set_array(val)
        self.pixels.changed()
        if self.autoscale:
            self.pixels.autoscale() # Updates the colorbar
        self.ax.figure.canvas.draw()

    def add_colorbar(self, label=''):
        self.colorbar = self.ax.figure.colorbar(self.pixels, label=label)

    def set_limits_minmax(self, zmin, zmax):
        """
        Set the color scale limits from min to max
        """
        self.pixels.set_clim(zmin, zmax)
        self.autoscale = False

    def reset_limits(self):
        """
        Reset to auto color scale limits
        """
        self.autoscale = True
        self.pixels.autoscale()

    def annotate_on_telescope_up(self):
        """
        Add an arrow indicating where "ON-Telescope-UP" is
        """
        if self._mapping is not None:
            axl = self._mapping.metadata['fOTUpX_l']
            ayl = self._mapping.metadata['fOTUpY_l']
            adx = self._mapping.metadata['fOTUpX_u'] - axl
            ady = self._mapping.metadata['fOTUpY_u'] - ayl
            text = "ON-Telescope UP"
            self.ax.arrow(axl, ayl, adx, ady, head_width=0.01,
                          head_length=0.01, fc='r', ec='r')
            self.ax.text(axl, ayl, text, fontsize=4, color='r',
                         ha='center', va='bottom')
        else:
            print("Cannot annotate, no mapping attached to class")

    def add_text_to_pixel(self, pixel, value, fmt=None, size=3):
        """
        Add a text label to a single pixel

        Parameters
        ----------
        pixel : int
        value : str or float
        fmt : str
            String/float formatting expression
        size : int
            Font size
        """
        pos_x = self.xpix[pixel]
        pos_y = self.ypix[pixel]
        if fmt:
            val = fmt.format(value)
        self.ax.text(pos_x, pos_y, value, fontsize=size,
                     color='w', ha='center')

    def add_pixel_text(self, values, fmt=None, size=3):
        """
        Add a text label to each pixel

        Parameters
        ----------
        values : ndarray
        fmt : str
            String/float formatting expression
        size : int
            Font size
        """
        assert values.size == self.n_pixels
        for pixel in range(self.n_pixels):
            self.add_text_to_pixel(pixel, values[pixel], fmt, size)

    def annotate_tm_edge_label(self):
        """
        Annotate each of the TMs on the top and bottom of the camera
        """
        if self._mapping is not None:
            kw = dict(fontsize=6, color='black', ha='center')
            m = self._mapping
            pix_size = self._mapping.metadata['size']
            f_tm_top = lambda g: m.ix[m.ix[g.index]['row'].idxmax(), 'slot']
            f_tm_bottom = lambda g: m.ix[m.ix[g.index]['row'].idxmin(), 'slot']
            tm_top = np.unique(m.groupby('col').agg(f_tm_top)['slot'])
            tm_bottom = np.unique(m.groupby('col').agg(f_tm_bottom)['slot'])
            for tm in tm_top:
                df = m.loc[m['slot'] == tm]
                ypix = df['ypix'].max() + pix_size * 0.7
                xpix = df['xpix'].mean()
                tm_txt = "TM{:02d}".format(tm)
                self.ax.text(xpix, ypix, tm_txt, va='bottom', **kw)
            for tm in tm_bottom:
                df = m.loc[m['slot'] == tm]
                ypix = df['ypix'].min() - pix_size * 0.7
                xpix = df['xpix'].mean()
                tm_txt = "TM{:02d}".format(tm)
                self.ax.text(xpix, ypix, tm_txt, va='top', **kw)
        else:
            print("Cannot annotate, no mapping attached to class")

    @classmethod
    def from_mapping(cls, mapping, **kwargs):
        """
        Generate the class from a CHECLabPy mapping dataframe

        Parameters
        ----------
        mapping : `pandas.DataFrame`
            The mapping for the pixels stored in a pandas DataFrame. Can be
            obtained from either of these options:

            CHECLabPy.io.TIOReader.mapping
            CHECLabPy.io.ReaderR0.mapping
            CHECLabPy.io.ReaderR1.mapping
            CHECLabPy.io.DL1Reader.mapping
            CHECLabPy.utils.mapping.get_clp_mapping_from_tc_mapping
        kwargs
            Arguments passed to `CHECLabPy.plottong.setup.Plotter`

        Returns
        -------
        `CameraImage`

        """
        xpix = mapping['xpix'].values
        ypix = mapping['ypix'].values
        size = mapping.metadata['size']
        image = cls(xpix, ypix, size, **kwargs)
        image._mapping = mapping
        return image

    @classmethod
    def from_tc_mapping(cls, tc_mapping, **kwargs):
        """
        Generate the class using the TargetCalib Mapping Class
        Parameters
        ----------
        tc_mapping : `target_calib.Mapping`
        kwargs
            Arguments passed to `CHECLabPy.plottong.setup.Plotter`

        Returns
        -------
        `CameraImage`

        """
        mapping = get_clp_mapping_from_tc_mapping(tc_mapping)
        return cls.from_mapping(mapping, **kwargs)

    @classmethod
    def from_camera_version(cls, camera_version, single=False, **kwargs):
        """
        Generate the class using the camera version (required TargetCalib)

        Parameters
        ----------
        camera_version : str
            Version of the camera (e.g. "1.0.1" corresponds to CHEC-S)
        single : bool
            Designate if it is just a single module you wish to plot
        kwargs
            Arguments passed to `CHECLabPy.plottong.setup.Plotter`

        Returns
        -------
        `CameraImage`

        """
        from target_calib import CameraConfiguration
        config = CameraConfiguration(camera_version)
        tc_mapping = config.GetMapping(single)
        return cls.from_tc_mapping(tc_mapping, **kwargs)

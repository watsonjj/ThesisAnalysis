from ThesisAnalysis.plotting.setup import ThesisPlotter
from ThesisAnalysis.plotting.camera import CameraImage
from ThesisAnalysis import get_data, get_plot, ThesisHDF5Reader
import numpy as np
from ctapipe.instrument import TelescopeDescription
from ctapipe.instrument.camera import _get_min_pixel_seperation
from astropy import units as u
from scipy.interpolate import griddata
from scipy import optimize
from ctapipe.visualization import CameraDisplay
from functools import partial
from matplotlib.ticker import AutoMinorLocator
from IPython import embed


class Coordinates:
    def __init__(self, mapping):
        foclen = 2.283 * u.m
        pix_pos = np.vstack([
            mapping['xpix'].values,
            mapping['ypix'].values
        ]) * u.m
        self.geom = TelescopeDescription.guess(*pix_pos, foclen).camera

        self.pix_x = mapping['xpix'].values
        self.pix_y = mapping['ypix'].values

        self.pix_x_u = np.unique(self.pix_x)
        self.pix_y_u = np.unique(self.pix_y)[::-1]
        self.pix_x_mg, self.pix_y_mg = np.meshgrid(self.pix_x_u, self.pix_y_u)
        self.xi = np.linspace(self.pix_x.min(), self.pix_x.max(), 1000)
        self.yi = np.linspace(self.pix_y.min(), self.pix_y.max(), 1000)[::-1]
        self.xi_mg, self.yi_mg = np.meshgrid(self.xi, self.yi)

    def get_gridded_data(self, data):
        xy = (self.pix_x, self.pix_y)
        xyi = (self.pix_x_u[None, :], self.pix_y_u[:, None])
        gd = griddata(xy, data, xyi, method='cubic')
        gd = np.ma.masked_invalid(gd)
        gd = np.ma.filled(gd, 0)
        gd[:8, :8] = 0
        gd[-8:, :8] = 0
        gd[-8:, -8:] = 0
        gd[:8, -8:] = 0
        return gd

    def get_gridded_data_i(self, data):
        xy = (self.pix_x, self.pix_y)
        xyi = (self.xi[None, :], self.yi[:, None])
        gd = griddata(xy, data, xyi, method='cubic')
        gd = np.ma.masked_invalid(gd)
        gd = np.ma.filled(gd, 0)
        return gd


class Gaussian2DFitter:
    @staticmethod
    def _fit_function(xy, amplitude, xo, yo, sigma, offset):
        x, y = xy
        xo = float(xo)
        yo = float(yo)
        g = offset + amplitude * np.exp(
            - ((((x - xo) ** 2) / (2 * sigma ** 2)) +
               (((y - yo) ** 2) / (2 * sigma ** 2))))
        return g.ravel()

    def fit(self, x, y, data):
        minsep = _get_min_pixel_seperation(x, y)
        p0 = (data.max(), x.mean(), y.mean(),
              minsep, np.median(data))
        bounds = ([0, x.min(), y.min(), 0, -np.inf],
                  [np.inf, x.max(), y.max(), np.inf, np.inf])
        popt, pcov = optimize.curve_fit(self._fit_function, (x, y), data,
                                        p0=p0, bounds=bounds)
        coeff = popt

        return coeff

    def get_curve(self, x, y, coeff):
        curve = self._fit_function((x, y), *coeff)
        curve = np.reshape(curve, x.shape)
        return curve

    def get_volume(self, coords, coeff, radius=np.inf):
        x, y = coords.xi_mg, coords.yi_mg
        curve = self.get_curve(x, y, coeff)
        curve_bs = curve - curve.min()

        x0, y0 = coeff[1], coeff[2]
        r = np.sqrt((x - x0) ** 2 + (y - y0) ** 2)
        curve_ma = np.ma.masked_where(r > radius, curve_bs)

        v = np.trapz(np.trapz(curve_ma, np.unique(x), 0), np.unique(y))
        return v

    def find_containment_radius(self, coords, coeff, containment=0.8):
        v_full = self.get_volume(coords, coeff)
        v_containment = containment * v_full
        v_partial = partial(self.get_volume, coords=coords, coeff=coeff)

        def v_fit(radius):
            return np.abs(v_partial(radius=radius) - v_containment)

        x0 = (coeff[3])
        res = optimize.minimize(v_fit, x0=x0, method='Nelder-Mead', tol=1e-6)
        return res.x[0]


class Image1DProjection(ThesisPlotter):
    def create(self, coords, data, coeff, fitter, axis):
        di = coords.get_gridded_data(data)
        df = fitter.get_curve(coords.xi_mg, coords.yi_mg, coeff)

        argmax_x = di.max(axis=1).argmax()
        argmax_y = di.max(axis=0).argmax()
        argmaxf_x = df.max(axis=1).argmax()
        argmaxf_y = df.max(axis=0).argmax()

        # embed()

        if axis == 0:
            di_1d = di[argmax_x]
            df_1d = df[argmaxf_x]
        else:
            di_1d = di[:, argmax_y]
            df_1d = df[:, argmaxf_y]


        if axis == 0:
            x_pixels = coords.pix_x_u
            x_plot = coords.xi
            axis_txt = 'X Position'
        else:
            x_pixels = coords.pix_y_u
            x_plot = coords.yi
            axis_txt = 'Y Position'

        minsep = np.diff(x_pixels)[0]#_get_min_pixel_seperation(coords.pix_x, coords.pix_y)
        hx = []
        hy =[]
        s = 0
        for i, (x, y) in enumerate(zip(x_pixels, di_1d)):
            if i % 8 == 0:
                hx.extend([x - minsep/2, x - minsep/2, x - minsep/2, x + minsep/2])
                hy.extend([np.nan, 0, y, y])
                s = x - minsep/2
            elif (i+1) % 8 == 0:
                hx.extend([x - minsep/2, x + minsep/2, x + minsep/2, s])
                hy.extend([y, y, 0, 0])
            else:
                hx.extend([x - minsep/2, x + minsep/2])
                hy.extend([y, y])

        color = next(self.ax._get_lines.prop_cycler)['color']
        self.ax.fill_between(hx, hy, np.zeros(len(hy)), linewidth=0.4, color=color)
        # self.ax.axhline(0, color='grey', linewidth=0.5, antialiased=False)

        f = np.s_[df_1d.argmax() - 100:df_1d.argmax() + 100]
        color = next(self.ax._get_lines.prop_cycler)['color']
        self.ax.plot(x_plot[f], df_1d[f], linewidth=0.5, color=color
                     )

        self.ax.set_xlabel(r"{} $(\degree)$".format(axis_txt))
        self.ax.set_ylabel("Excess Baseline RMS (p.e.)")

        amplitude, x0, y0, sigma, offset = coeff
        radius = fitter.find_containment_radius(coords, coeff, 0.8)
        if axis == 0:
            x0 = x0
        else:
            x0 = y0
        xl = x0 - radius
        xr = x0 + radius

        self.ax.axvline(xl, color='black', lw=0.5)
        self.ax.axvline(xr, color='black', lw=0.5)
        self.ax.text(xr + 0.2, np.max(df_1d) * 0.7, "80% Volume\nContainment", color='black')

        minor_locator = AutoMinorLocator(10)
        self.ax.xaxis.set_minor_locator(minor_locator)
        # self.ax.yaxis.set_minor_locator(minor_locator)

        # self.ax.axes.set_xlim(-0.8, 0.8)


class ZoomedImagePlotter(ThesisPlotter):
    def create(self, image, coords, title, coeff, fitter):
        df = fitter.get_curve(coords.xi_mg, coords.yi_mg, coeff)

        camera = CameraDisplay(coords.geom, ax=self.ax,
                               image=image,
                               cmap='viridis')
        camera.add_colorbar()
        camera.colorbar.set_label("Excess Baseline RMS (p.e.)")
        camera.image = image

        amplitude, x0, y0, sigma, offset = coeff
        radius = fitter.find_containment_radius(coords, coeff, 0.8)
        x80 = x0 + radius
        y80 = y0
        z = offset + amplitude * np.exp(
            - ((((x80 - x0) ** 2) / (2 * sigma ** 2)) +
               (((y80 - y0) ** 2) / (2 * sigma ** 2))))

        CS = self.ax.contour(coords.xi_mg, coords.yi_mg, df,
                             linewidths=0.5, colors='red', levels=[z])
        text = ("80% Containment \n"
                r"($\SI{{{:.3}}}{{\degree}}$)").format(radius)
        self.ax.text(x80, y80, text, color='red')

        self.ax.axis([-1.75, 1, -1.5, 1.5])

        camera.axes.set_xlabel(r"X Position ($\degree$)")
        camera.axes.set_ylabel(r"Y Position ($\degree$)")
        camera.axes.set_title("")


def main():
    input_path = get_data("jupiter.h5")
    with ThesisHDF5Reader(input_path) as reader:
        df = reader.read("data")
        mapping = reader.read_mapping()
        plate_scale = reader.read_metadata()['plate_scale']

    mapping['xpix'] /= plate_scale
    mapping['ypix'] /= plate_scale
    mapping.metadata['size'] /= plate_scale

    coords = Coordinates(mapping)

    data = df[1, 0.0]
    fitter = Gaussian2DFitter()
    coeff = fitter.fit(coords.pix_x, coords.pix_y, data)

    p_1d = Image1DProjection(sidebyside=True)
    p_1d.create(coords, data, coeff, fitter, 0)
    p_1d.save(get_plot("jupiter/1d_projection_x.pdf"))

    p_1d = Image1DProjection(sidebyside=True)
    p_1d.create(coords, data, coeff, fitter, 1)
    p_1d.save(get_plot("jupiter/1d_projection_y.pdf"))

    p_zoom = ZoomedImagePlotter()
    p_zoom.create(data, coords, "1mirror_0.0deg - Zoomed and Contoured", coeff,
                  fitter)
    p_zoom.save(get_plot("jupiter/contour.pdf"))

    di = coords.get_gridded_data(data)
    argmax_x = di.max(axis=1).argmax()
    argmax_y = di.max(axis=0).argmax()
    pixels1 = mapping.loc[mapping['row'] == (47 - argmax_x)]['pixel']
    pixels2 = mapping.loc[mapping['col'] == argmax_y]['pixel']
    # embed()
    p_image = CameraImage.from_mapping(mapping)
    p_image.image = df[1, 0]
    p_image.add_colorbar("Excess Baseline RMS (p.e.)")
    p_image.highlight_pixels(np.concatenate([pixels1, pixels2]), 'white', 0.2, 1)
    p_image.save(get_plot("jupiter/image_mirror1_deg0.pdf"))

    # p_image = CameraImage.from_mapping(mapping)
    # p_image.image = df[1, 2]
    # p_image.add_colorbar("Excess Baseline RMS (p.e.)")
    # p_image.save(get_plot("jupiter/image_mirror1_deg2.pdf"))
    #
    # p_image = CameraImage.from_mapping(mapping)
    # p_image.image = df[2, 0]
    # p_image.add_colorbar("Excess Baseline RMS (p.e.)")
    # p_image.save(get_plot("jupiter/image_mirror2_deg0.pdf"))
    #
    # p_image = CameraImage.from_mapping(mapping)
    # p_image.image = df[2, 2]
    # p_image.add_colorbar("Excess Baseline RMS (p.e.)")
    # p_image.save(get_plot("jupiter/image_mirror2_deg2.pdf"))
    #
    # p_image = CameraImage.from_mapping(mapping)
    # p_image.image = df[2, 3.5]
    # p_image.add_colorbar("Excess Baseline RMS (p.e.)")
    # p_image.save(get_plot("jupiter/image_mirror3_deg3p5.pdf"))


if __name__ == '__main__':
    main()
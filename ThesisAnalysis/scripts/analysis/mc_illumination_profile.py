from ThesisAnalysis import get_data, get_plot, \
    ThesisHDF5Reader, ThesisHDF5Writer
from ThesisAnalysis.plotting.setup import ThesisPlotter
from ThesisAnalysis.plotting.camera import CameraImage
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from numpy.polynomial.polynomial import polyfit, polyval


class IlluminationProfile:
    def __init__(self):
        self.camera_radius = 1  # 1000000000
        self.lightsource_focalplane_seperation = 1.552
        self.pixel_area = 0.00623

        path = get_data("transmission_pmma_vs_theta_20150422.dat")
        self.angular_response_array = np.loadtxt(path, unpack=True)

    def distance_to_radial_position(self, x):
        r = self.camera_radius
        dc = self.lightsource_focalplane_seperation
        dz = np.sqrt(x**2 + (dc + r - np.sqrt(r**2 - x**2))**2)
        return dz

    def viewing_angle(self, x):
        r = self.camera_radius
        dz = self.distance_to_radial_position(x)
        theta = np.arcsin(x / dz)
        alpha = np.arcsin(x / r)
        beta = theta + alpha
        return beta

    def viewing_area(self, x):
        beta = self.viewing_angle(x)
        viewing_area = self.pixel_area * np.cos(beta)
        return viewing_area

    def angular_response(self, angle):
        theta = angle * np.pi / 180
        x, y = self.angular_response_array
        response = np.interp(theta, x, y)
        return response

    def angular_response_at_radial_position(self, x):
        angle = self.viewing_angle(x)
        response = self.angular_response(angle)
        return response

    def get_illumination_correction(self, x):
        dc = self.lightsource_focalplane_seperation
        dz = self.distance_to_radial_position(x)
        dz_corr = dc**2 / dz**2

        pa = self.pixel_area
        pz = self.viewing_area(x)
        pz_corr = pz / pa

        ang_corr = self.angular_response_at_radial_position(x)

        correction = dz_corr * pz_corr# * ang_corr
        return correction


class PixelScatter(ThesisPlotter):
    def __init__(self):
        super().__init__()

        self.df_list = []

        self.fig = plt.figure(figsize=self.get_figsize())
        self.data_ax = self.fig.add_axes((.1, .3, .8, .6))
        self.data_ax.set_xticklabels([])
        self.res_ax = self.fig.add_axes((.1, .1, .8, .2))

    def plot(self, x, y, params):
        self.data_ax.scatter(x, y, s=0.5)

        xf = np.linspace(x.min(), x.max(), 100)
        yf = polyval(xf, params)
        self.data_ax.plot(xf, yf, color='red')

        ip = IlluminationProfile()
        yfm = ip.get_illumination_correction(xf) * yf.max()
        self.data_ax.plot(xf, yfm, color='green')

        # Residuals
        self.res_ax.axhline(0, ls='--', c='red', alpha=0.3, lw=0.5)
        corrections = polyval(x, params)
        yc = y / corrections - 1
        self.res_ax.scatter(x, yc, s=0.5)

        self.data_ax.set_ylabel("Photoelectrons", labelpad=13)
        self.res_ax.set_ylabel("Residuals")
        self.res_ax.set_xlabel("Distance from Camera Centre (m)")


def main():
    with ThesisHDF5Reader(get_data("mc_illumination_profile.h5")) as reader:
        df = reader.read("data")
        mapping = reader.read_mapping()
        metadata = reader.read_metadata()

    true = df['true'].values
    dist = df['distance'].values
    n_events = metadata['n_events']

    params = polyfit(dist, true, [0, 2])
    params_norm = params/polyval(0, params)
    pixel_corrections = polyval(dist, params_norm)

    df_corr = pd.DataFrame(dict(
        correction=pixel_corrections
    ))
    df_params = pd.DataFrame(params_norm)

    path = get_data("mc_illumination_profile_correction.h5")
    with ThesisHDF5Writer(path) as writer:
        writer.write(correction=df_corr, params=df_params)
        writer.write_mapping(mapping)

    p_dvt = PixelScatter()
    p_dvt.plot(dist, true, params)
    p_dvt.save(get_plot("mc_illumination_profile/mc_illumination_profile.pdf"))

    p_f = CameraImage.from_mapping(mapping)
    p_f.image = pixel_corrections
    p_f.add_colorbar("Illumination Profile Correction")
    p_f.save(get_plot("mc_illumination_profile/mc_illumination_profile_camera.pdf"))


if __name__ == '__main__':
    main()

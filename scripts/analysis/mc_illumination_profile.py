import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
import seaborn as sns
from CHECLabPy.core.io import DL1Reader
from CHECLabPy.plotting.setup import Plotter
from CHECLabPy.plotting.camera import CameraImage
from numpy.polynomial.polynomial import polyfit, polyval
from IPython import embed


class IlluminationProfile:
    def __init__(self):
        self.camera_radius = 1
        self.lightsource_focalplane_seperation = 1.552
        self.pixel_area = 0.00623

        self.angular_response_array = np.loadtxt("/Users/Jason/Dropbox/DropboxDocuments/University/Oxford/Reports/Thesis_data/misc/transmission_pmma_vs_theta_20150422.dat", unpack=True)

    def distance_to_radial_position(self, x):
        r = self.camera_radius
        dc = self.lightsource_focalplane_seperation
        dz = np.sqrt(x**2 + (dc + r - np.sqrt(r**2 + x**2))**2)
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

        correction = dz_corr * pz_corr * ang_corr
        return correction


class PixelScatter(Plotter):
    def __init__(self, xlabel='', ylabel='', zlabel='', title=''):
        super().__init__()

        self.xlabel = xlabel
        self.ylabel = ylabel
        self.zlabel = zlabel
        self.title = title

        self.df_list = []

    def plot(self, x, y, z):
        # y = 1 / np.sqrt(y)

        params = polyfit(x, y, [0, 2])

        # y /= polyval(x, params)
        # y *= polyval(0, params)
        # embed()

        cm = plt.cm.get_cmap('viridis')
        sc = self.ax.scatter(x, y, c=z, cmap=cm, s=0.5)

        xf = np.linspace(x.min(), x.max(), 10)
        yf = polyval(xf, params)
        self.ax.plot(xf, yf)

        ip = IlluminationProfile()
        yf = ip.get_illumination_correction(xf) * yf.max()
        self.ax.plot(xf, yf)

        x, y = np.loadtxt("/Users/Jason/Downloads/tmp_true_pe_dist.txt", unpack=True)
        y *= yf.max()
        self.ax.plot(x, y)

        cb = self.fig.colorbar(sc)
        cb.set_label(self.zlabel)

        self.ax.set_title(self.title)
        self.ax.set_xlabel(self.xlabel)
        self.ax.set_ylabel(self.ylabel)

        return params/polyval(0, params)


def main():
    # input_file = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/1_flat_focal_plane/Run43489_dl1.h5"
    input_file = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/2_no_noise/Run43489_dl1.h5"

    reader = DL1Reader(input_file)
    mapping = reader.mapping
    poi = np.arange(2048)
    pixel, true = reader.select_columns(['pixel', 'mc_true'])
    xpix = mapping['xpix']
    ypix = mapping['ypix']
    dist = np.sqrt(xpix ** 2 + ypix ** 2)

    true_p = true.values.reshape((1000, 2048)).mean(0)

    params = polyfit(dist, true, [0, 2])
    
    with pd.HDFStore("")



    p_mvt = PixelScatter("Measured", "True", "Distance from camera center")
    p_dvt = PixelScatter("Distance from camera center", "True", "Measured")
    p_dvm = PixelScatter("Distance from camera center", "Measured", "True")

    # p_mvt.plot(measured_p, true_p, dist)
    calib_params = p_dvt.plot(dist, true_p, measured_p)
    # p_dvm.plot(dist, measured_p, true_p)

    p_mvt.save("mvt")
    p_dvt.save("dvt")
    p_dvm.save("dvm")

    xpix = mapping['xpix'].values
    ypix = mapping['ypix'].values
    dist = np.sqrt(xpix ** 2 + ypix ** 2)
    f = polyval(dist, calib_params)
    print(calib_params)

    p_f = CameraImage.from_mapping(mapping)
    p_f.image = f
    p_f.add_colorbar()
    p_f.save("f.pdf")

    np.savetxt("illumination_correction_mc.txt", f)

if __name__ == '__main__':
    main()

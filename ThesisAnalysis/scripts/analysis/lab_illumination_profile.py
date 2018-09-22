from ThesisAnalysis.plotting.camera import CameraImage
from ThesisAnalysis import get_data, ThesisHDF5Writer, get_plot
import pandas as pd
import numpy as np
import os
from numpy.polynomial.polynomial import polyfit, polyval
from CHECLabPy.utils.mapping import get_clp_mapping_from_version
from IPython import embed


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

    def fold_laser_profile(self, vy, v, ypix):
        c, m = polyfit(vy, v, 1)

        dz = self.distance_to_radial_position(ypix)
        theta = np.arcsin(ypix/dz)
        cy = self.lightsource_focalplane_seperation * np.tan(theta)
        cv = polyval(cy, (c, m))
        return cv


def process(camera):
    input_file = get_data("lab_illumination_profile.txt")

    df = pd.read_csv(input_file, sep=' ')

    ip = IlluminationProfile()

    vmapping = get_clp_mapping_from_version("1.1.0")
    if camera == "checm":
        mapping = get_clp_mapping_from_version("1.0.0")
    else:
        mapping = get_clp_mapping_from_version("1.1.0")

    vy = vmapping['ypix'].values
    ypix = mapping['ypix'].values

    pixel = df['Pixel'].values
    laser_correction = 1/df['LaserCorrection'].values
    geom_correction = 1/df['FlatCorrection'].values
    total_correction = 1/df['TotalCorrection'].values

    # laser_correction = ip.fold_laser_profile(vy, laser_correction, ypix)

    xpix = mapping['xpix'].values
    ypix = mapping['ypix'].values
    r = np.sqrt(xpix**2 + ypix**2)
    geom_correction = ip.get_illumination_correction(r)
    total_correction = geom_correction * laser_correction
    # embed()

    plot_dir = get_plot("{}_illumination_profile".format(camera))

    p_image_laser = CameraImage.from_mapping(mapping)
    p_image_laser.image = laser_correction
    p_image_laser.add_colorbar("Laser Correction")
    path = os.path.join(plot_dir, "laser_correction.pdf")
    p_image_laser.save(path)

    p_image_geom = CameraImage.from_mapping(mapping)
    p_image_geom.image = geom_correction
    p_image_geom.add_colorbar("Geometry Correction")
    path = os.path.join(plot_dir, "geom_correction.pdf")
    p_image_geom.save(path)

    p_image_total = CameraImage.from_mapping(mapping)
    p_image_total.image = total_correction
    p_image_total.add_colorbar("Total Correction")
    path = os.path.join(plot_dir, "total_correction.pdf")
    p_image_total.save(path)

    df_corr = pd.DataFrame(dict(
        pixel=pixel,
        correction=total_correction,
    ))

    path = get_data("{}_illumination_profile_correction.h5".format(camera))
    with ThesisHDF5Writer(path) as writer:
        writer.write(correction=df_corr)
        writer.write_mapping(p_image_laser._mapping)


def main():
    camera = "checs"
    process(camera)

    camera = "checm"
    process(camera)


if __name__ == '__main__':
    main()

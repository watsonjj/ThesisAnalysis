from ThesisAnalysis import get_data, ThesisHDF5Writer
from CHECLabPy.core.io import DL1Reader
from ctapipe.image import tailcuts_clean
from ctapipe.image.hillas import HillasParameterizationError, \
    hillas_parameters
from CHECLabPy.plotting.camera import CameraImage
from ctapipe.instrument import TelescopeDescription
from astropy import units as u
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from pandas.errors import PerformanceWarning
import warnings
from tqdm import tqdm
from glob import glob

from IPython import embed


def process(input_paths, tailcuts, plate_scale, output_path, plot=False):
    d_list = []
    mapping = None
    desc0 = "Looping over files"
    desc1 = "Looping over events"
    n_files = len(input_paths)

    itotal = 0
    imax = 20000

    for ifile, input_path in tqdm(enumerate(input_paths), total=n_files, desc=desc0):
        reader = DL1Reader(input_path)
        mapping = reader.mapping
        mapping['xpix'] /= plate_scale
        mapping['ypix'] /= plate_scale
        mapping.metadata['size'] /= plate_scale
        ci = CameraImage.from_mapping(mapping)

        foclen = 2.283 * u.m
        pix_pos = np.vstack([
            mapping['xpix'].values,
            mapping['ypix'].values
        ]) * u.m
        geom = TelescopeDescription.guess(*pix_pos, foclen).camera

        n_events = reader.n_events
        for iev, df in tqdm(enumerate(reader.iterate_over_events()), total=n_events, desc=desc1):
            image = df['charge'].values
            peakpos = df['ctapipe_peakpos'].values
            try:
                mc_true = df['mc_true'].values
            except KeyError:
                mc_true = np.zeros(image.shape)

            tc = tailcuts_clean(geom, image, *tailcuts)
            if not tc.any():
                continue
            if tc.sum() <= 6:
                continue
            cleaned_image = np.ma.masked_array(image, mask=~tc)
            cleaned_peakpos = np.ma.masked_array(peakpos, mask=~tc)

            try:
                hillas = hillas_parameters(geom, cleaned_image)
            except HillasParameterizationError:
                continue

            if np.isnan(hillas.width):
                continue

            if plot:
                ci.image = cleaned_image
                ci.highlight_pixels(np.arange(2048), 'black', 0.2, 1)
                plt.pause(1)

            d_list.append(dict(
                ifile=ifile,
                iev=iev,
                image=image,
                peakpos=peakpos,
                tailcuts=tc,
                mc_true=mc_true,
                size=hillas.size,
                cen_x=hillas.cen_x.value,
                cen_y=hillas.cen_y.value,
                length=hillas.length.value,
                width=hillas.width.value,
                r=hillas.r.value,
                phi=hillas.phi.value,
                psi=hillas.psi.value,
                miss=hillas.miss.value,
                skewness=hillas.skewness,
                kurtosis=hillas.kurtosis
            ))
            itotal += 1
        if itotal >= imax:
            break

    df = pd.DataFrame(d_list)

    with ThesisHDF5Writer(output_path) as writer:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', PerformanceWarning)
            writer.write(data=df)
        writer.write_mapping(mapping)
        writer.write_metadata(
            tailcuts=tailcuts,
            n_files=len(input_paths),
        )



def main():
    input_paths = [
        "/Volumes/gct-jason/thesis_data/checm/cherenkov/Run05477_dl1.h5"
    ]
    tailcuts = (17, 8)
    plate_scale = 40.344e-3
    output_path = "/Volumes/gct-jason/thesis_data/checm/cherenkov/Run05477_dl1b.h5"
    process(input_paths, tailcuts, plate_scale, output_path)

    input_paths = [
        "/Volumes/gct-jason/thesis_data/checm/cherenkov/meudon_cr/proton_dl1.h5"
    ]
    tailcuts = (17, 8)
    plate_scale = 40.344e-3
    output_path = "/Volumes/gct-jason/thesis_data/checm/cherenkov/meudon_cr/proton_dl1b.h5"
    process(input_paths, tailcuts, plate_scale, output_path)

    input_paths = [
        "/Volumes/gct-jason/thesis_data/checm/cherenkov/meudon_cr/proton_heidefix_dl1.h5"
    ]
    tailcuts = (17, 8)
    plate_scale = 40.344e-3
    output_path = "/Volumes/gct-jason/thesis_data/checm/cherenkov/meudon_cr/proton_heidefix_dl1b.h5"
    process(input_paths, tailcuts, plate_scale, output_path)

    input_paths = glob(
        "/Volumes/gct-jason/thesis_data/checs/mc/onsky/gamma/v2/Run*_dl1.h5"
    )
    tailcuts = (10, 2)
    plate_scale = 39.6e-3
    output_path = "/Volumes/gct-jason/thesis_data/checs/mc/onsky/proton/v2/checs_gamma_dl1b.h5"
    process(input_paths, tailcuts, plate_scale, output_path)

    input_paths = glob(
        "/Volumes/gct-jason/thesis_data/checs/mc/onsky/proton/v2/Run*_dl1.h5"
    )
    tailcuts = (10, 2)
    plate_scale = 39.6e-3
    output_path = "/Volumes/gct-jason/thesis_data/checs/mc/onsky/proton/v2/checs_proton_dl1b.h5"
    process(input_paths, tailcuts, plate_scale, output_path)


if __name__ == '__main__':
    main()
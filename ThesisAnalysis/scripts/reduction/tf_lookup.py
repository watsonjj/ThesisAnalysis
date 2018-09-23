from ThesisAnalysis import get_data, ThesisHDF5Writer
import numpy as np
import pandas as pd
from astropy.io import fits
from IPython import embed


def process_t5(input_path, output_path, poi):
    hdu1 = fits.open(input_path)

    n_cells = int(hdu1[0].header["CELLS"])
    n_pnts = int(hdu1[0].header["PNTS"])
    min_ = hdu1[0].header["MIN"]
    step = hdu1[0].header["STEP"]

    x = min_ + np.arange(n_pnts) * step

    data_flat = hdu1[1].data[poi][0] * 2.5/4096 * 1000

    df_x = pd.DataFrame(dict(
        x=x,
    ))
    df_y = pd.DataFrame(dict(
        y=data_flat,
    ))

    with ThesisHDF5Writer(output_path) as writer:
        writer.write(
            x=df_x,
            y=df_y
        )
        writer.write_metadata(
            n_cells=n_cells,
            n_pnts=n_pnts
        )


def process_tc(input_path, output_path, poi):
    hdu1 = fits.open(input_path)

    n_cells = int(hdu1[0].header["CELLS"])
    n_pnts = int(hdu1[0].header["PNTS"])
    scale = None
    offset = None
    try:
        scale = hdu1[0].header["SCALE"]
        offset = hdu1[0].header["OFFSET"]
    except:
        pass

    x = np.array(hdu1[2].data.astype(np.float))

    # data_flat = (hdu1[1].data[poi][0] - offset) / scale
    data_flat = hdu1[1].data[poi][0]
    if scale:
        data_flat = (data_flat - offset) / scale

    df_x = pd.DataFrame(dict(
        x=x,
    ))
    df_y = pd.DataFrame(dict(
        y=data_flat,
    ))

    with ThesisHDF5Writer(output_path) as writer:
        writer.write(
            x=df_x,
            y=df_y
        )
        writer.write_metadata(
            n_cells=n_cells,
            n_pnts=n_pnts
        )


def main():
    input_path = "/Volumes/gct-jason/thesis_data/checm/tf/Run00001-00050_tf.tcal"
    output_path = get_data("tf/t5_lookup.h5")
    poi = 0
    process_t5(input_path, output_path, poi)

    # input_path = "/Volumes/gct-jason/thesis_data/checs/lab/tf/SN0074_tf.tcal"
    input_path = "/Volumes/gct-jason/thesis_data/checs/lab/tf/4_tf_poly.tcal"
    output_path = get_data("tf/tc_lookup.h5")
    poi = 0
    process_tc(input_path, output_path, poi)

    input_path = "/Volumes/gct-jason/thesis_data/checs/lab/tf/2_tf_with_ped.tcal"
    output_path = get_data("tf/tc_direct_lookup.h5")
    poi = 0
    process_tc(input_path, output_path, poi)

if __name__ == '__main__':
    main()

from ThesisAnalysis import get_data, ThesisHDF5Writer, ThesisHDF5Reader
import numpy as np
import pandas as pd
from CHECLabPy.core.io import TIOReader
from CHECLabPy.waveform_reducers.cross_correlation import CrossCorrelation
from tqdm import tqdm


def process(r0_path, r1_path, output_path, poi,
            even_events=False, ff_path=None):

    r0_reader = TIOReader(r0_path)
    r1_reader = TIOReader(r1_path)
    n_events = r0_reader.n_events
    n_pixels = r0_reader.n_pixels
    n_samples = r0_reader.n_samples
    samples = np.arange(n_samples, dtype=np.uint16)

    mvtope = 1
    if ff_path:
        with ThesisHDF5Reader(ff_path) as reader:
            df = reader.read("data")
            gamma_q = df['gamma_q'].values[0]

        ref_path = r1_reader.reference_pulse_path
        cc = CrossCorrelation(n_pixels, n_samples,
                              reference_pulse_path=ref_path)
        mvtope = cc.get_pulse_height(gamma_q)

    df_list = []

    desc = "Looping over events"
    for r0, r1 in tqdm(zip(r0_reader, r1_reader), total=n_events, desc=desc):
        iev = r0_reader.index
        if even_events:
            if iev % 2:
                continue
        fci = np.asscalar(r0_reader.first_cell_ids[poi])

        r1 = r1 / mvtope

        df_list.append(pd.DataFrame(dict(
            iev=iev,
            fci=fci,
            isam=samples,
            r0=r0[poi],
            r1=r1[poi],
        )))

    df = pd.concat(df_list, ignore_index=True)

    with ThesisHDF5Writer(output_path) as writer:
        writer.write(data=df)
        writer.write_metadata(poi=poi)


def main():
    poi = 30
    r0_path = "/Volumes/gct-jason/thesis_data/checs/lab/pedestal/Pedestals.tio"
    r1_path = "/Volumes/gct-jason/thesis_data/checs/lab/pedestal/Pedestals_r1.tio"
    output_path = get_data("pedestal/pedestal_checs.h5")
    process(r0_path, r1_path, output_path, poi, True)

    poi = 30
    r0_path = "/Volumes/gct-jason/thesis_data/checs/lab/pedestal/Pedestals.tio"
    r1_path = "/Volumes/gct-jason/thesis_data/checs/lab/pedestal/Pedestals_r1_mV.tio"
    output_path = get_data("pedestal/pedestal_checs_mV.h5")
    process(r0_path, r1_path, output_path, poi, True)

    poi = 30
    r0_path = "/Volumes/gct-jason/thesis_data/checs/lab/pedestal/Pedestals.tio"
    r1_path = "/Volumes/gct-jason/thesis_data/checs/lab/pedestal/Pedestals_r1_mV.tio"
    output_path = get_data("pedestal/pedestal_checs_pe.h5")
    ff_path = get_data("ff_values.h5")
    process(r0_path, r1_path, output_path, poi, True, ff_path)

    poi = 30
    r0_path = "/Volumes/gct-jason/thesis_data/checm/pedestal/Run00053_r0.tio"
    r1_path = "/Volumes/gct-jason/thesis_data/checm/pedestal/Run00053_r1.tio"
    output_path = get_data("pedestal/pedestal_checm.h5")
    process(r0_path, r1_path, output_path, poi)

    poi = 30
    r0_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/r0/Run43510_r0.tio"
    r1_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_none/Run43510_r1.tio"
    output_path = get_data("pedestal/pedestal_pulse_checs.h5")
    process(r0_path, r1_path, output_path, poi)


if __name__ == '__main__':
    main()

from ThesisAnalysis import get_data, ThesisHDF5Writer
import numpy as np
import pandas as pd
from CHECLabPy.core.io import DL1Reader


def main():
    input_file = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/2_no_noise/Run43489_dl1.h5"

    reader = DL1Reader(input_file)
    mapping = reader.mapping
    pixel, true = reader.select_columns(['pixel', 'mc_true'])
    xpix = mapping['xpix'].values
    ypix = mapping['ypix'].values
    dist = np.sqrt(xpix ** 2 + ypix ** 2)

    n_events = reader.n_events
    true_p = true.values.reshape((n_events, 2048)).mean(0)

    df = pd.DataFrame(dict(
        distance=dist,
        true=true_p,
    ))

    with ThesisHDF5Writer(get_data("mc_illumination_profile.h5")) as writer:
        writer.write(data=df)
        writer.write_mapping(mapping)
        writer.write_metadata(n_events=n_events)


if __name__ == '__main__':
    main()

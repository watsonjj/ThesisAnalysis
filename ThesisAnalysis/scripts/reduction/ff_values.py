from ThesisAnalysis import get_data, ThesisHDF5Writer, ThesisHDF5Reader
from ThesisAnalysis.files import Lab_TFPoly
import pandas as pd
import numpy as np
from IPython import embed


def process(file, output_path):

    input_path = file.ff_path
    dead = file.dead

    with ThesisHDF5Reader(input_path) as reader:
        df = reader.read("data")
        ff_m = df['ff_m'].values
        ff_merr = df['ff_merr'].values
        mapping = reader.read_mapping()

    dead_mask = np.zeros(ff_m.size, dtype=np.bool)
    dead_mask[dead] = True

    ff_m_d = ff_m[~dead_mask]
    ff_merr_d = ff_merr[~dead_mask]

    w = 1/ff_merr_d

    gamma_q = np.average(ff_m_d, weights=w)
    gamma_q_err = np.sqrt(np.average((ff_m_d - gamma_q) ** 2, weights=w))

    # gamma_q = ff_m.mean()
    # gamma_q_err = ff_m.std()

    gamma_ff = gamma_q/ff_m

    df = pd.DataFrame(dict(
        gamma_q=gamma_q,
        gamma_ff=gamma_ff,
        gamma_q_err=gamma_q_err,
    ))

    with ThesisHDF5Writer(output_path) as writer:
        writer.write(data=df)
        writer.write_mapping(mapping)


def main():
    file = Lab_TFPoly()
    output_path = get_data("ff_values.h5")
    process(file, output_path)


if __name__ == '__main__':
    main()

from ThesisAnalysis import get_data, ThesisHDF5Writer
import numpy as np
import pandas as pd
from CHECLabPy.core.io import TIOReader
from CHECLabPy.waveform_reducers.ctapipe import \
    CtapipeNeighbourPeakIntegrator


def process(r0_path, r1_path, r1pe_path, output_path, eoi):

    r0_reader = TIOReader(r0_path)
    r1_reader = TIOReader(r1_path)
    r1pe_reader = TIOReader(r1pe_path)

    r0 = r0_reader[eoi]
    r1 = r1_reader[eoi]
    r1pe = r1pe_reader[eoi]

    n_pixels = r1_reader.n_pixels
    n_samples = r1_reader.n_samples
    mapping = r1_reader.mapping

    e = CtapipeNeighbourPeakIntegrator(n_pixels, n_samples, mapping=mapping)
    window = e.integrator.get_window_from_waveforms(r1pe[None, :])[0]
    r0_charge = e.integrator.extract_from_window(r0[None, :], window)[0]
    r1_charge = e.integrator.extract_from_window(r1[None, :], window)[0]
    r1pe_charge = e.integrator.extract_from_window(r1pe[None, :], window)[0]

    df = pd.DataFrame(dict(
        iev=eoi,
        pixel=np.arange(n_pixels),
        r0=r0_charge,
        r1=r1_charge,
        r1pe=r1pe_charge,
    ))

    with ThesisHDF5Writer(output_path) as writer:
        writer.write(data=df)
        writer.write_mapping(mapping)
        writer.write_metadata(n_pixels=n_pixels)


def main():
    eoi = 89
    r0_path = "/Volumes/gct-jason/thesis_data/checm/cherenkov/Run05477_r0.tio"
    r1_path = "/Volumes/gct-jason/thesis_data/checm/cherenkov/Run05477_r1_adc.tio"
    r1pe_path = "/Volumes/gct-jason/thesis_data/checm/cherenkov/Run05477_r1.tio"
    output_path = get_data("cherenkov_pedestal_comparison.h5")
    process(r0_path, r1_path, r1pe_path, output_path, eoi)


if __name__ == '__main__':
    main()

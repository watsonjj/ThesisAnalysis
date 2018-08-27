from ThesisAnalysis import get_data, ThesisHDF5Writer
import numpy as np
import pandas as pd
from target_calib import CameraConfiguration


def process(input_path, output_path):
    data = np.loadtxt(input_path)

    df = pd.DataFrame(dict(
        before=data[0],
        after=data[-1]
    ))

    n_pixels, n_samples = data.shape
    reference_pulse_path = CameraConfiguration("1.1.0").GetReferencePulsePath()

    with ThesisHDF5Writer(output_path) as writer:
        writer.write(data=df)
        writer.write_metadata(
            n_pixels=n_pixels,
            n_samples=n_samples,
            reference_pulse_path=reference_pulse_path
        )


def main():
    input_path = "/Volumes/gct-jason/thesis_data/checs/lab/gain_matching/results_pixelamps.txt"
    output_path = get_data("before_after_gm.h5")
    process(input_path, output_path)


if __name__ == '__main__':
    main()

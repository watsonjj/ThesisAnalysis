from ThesisAnalysis import get_data, ThesisHDF5Writer, ThesisHDF5Reader
from ThesisAnalysis.files import Lab_TFPoly
import pandas as pd


def process(input_path, output_path):
    with ThesisHDF5Reader(input_path) as reader:
        df = reader.read("data")
        ff_m = df['ff_m'].values
        mapping = reader.read_mapping()

    df = pd.DataFrame(dict(
        gamma_q=ff_m.mean(),
        gamma_ff=ff_m.mean()/ff_m,
    ))

    with ThesisHDF5Writer(output_path) as writer:
        writer.write(data=df)
        writer.write_mapping(mapping)


def main():
    file = Lab_TFPoly()
    input_path = file.ff_path
    output_path = get_data("ff_values.h5")
    process(input_path, output_path)


if __name__ == '__main__':
    main()

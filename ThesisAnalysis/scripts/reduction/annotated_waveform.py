from ThesisAnalysis import get_data, ThesisHDF5Writer
from ThesisAnalysis.files import Lab_TFPoly
from CHECLabPy.core.io import TIOReader
import pandas as pd


def process(file, illumination, eoi, poi, output_path):
    input_path = file.get_run_with_illumination_r1(illumination)
    reader = TIOReader(input_path, max_events=1000)

    wf = reader[eoi][poi]

    df = pd.DataFrame(dict(
        wf=wf,
    ))

    with ThesisHDF5Writer(output_path) as writer:
        writer.write(data=df)


def main():
    file = Lab_TFPoly()
    illumination = 3
    eoi = 25
    poi = 888
    output_path = get_data("annotated_waveform/checs_3pe.h5")
    process(file, illumination, eoi, poi, output_path)



if __name__ == '__main__':
    main()

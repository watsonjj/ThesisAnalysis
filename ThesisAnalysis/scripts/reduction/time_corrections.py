from ThesisAnalysis import get_data, ThesisHDF5Writer
from ThesisAnalysis.files import Lab_Window, MCLab_Opct40_Window_5MHz, CHECM
from CHECLabPy.core.io import DL1Reader
import numpy as np
import pandas as pd


def process(file, output_path):
    input_path, _, _ = file.get_run_with_illumination(100)
    dead = file.dead
    reader = DL1Reader(input_path)
    n_pixels = reader.n_pixels
    mapping = reader.mapping
    pixel, iev, t_pulse = reader.select_columns(['pixel', 'iev', 't_pulse'])
    df = pd.DataFrame(dict(
        pixel=pixel,
        iev=iev,
        t_pulse=t_pulse,
    ))

    t_corr = np.zeros(n_pixels)

    df_dead = df.loc[~df['pixel'].isin(dead)].copy()
    df_dead['t_event'] = df_dead.groupby('iev').transform(np.mean)['t_pulse']
    df_dead['t_pulse_corr'] = df_dead['t_pulse'] - df_dead['t_event']
    df_mean = df_dead.groupby('pixel').mean()
    pixel = df_mean.index.values
    t_corr[pixel] = df_mean['t_pulse_corr'].values

    df = pd.DataFrame(dict(
        pixel=np.arange(n_pixels),
        t_corr=t_corr,
    ))

    with ThesisHDF5Writer(output_path) as writer:
        writer.write(data=df)
        writer.write_metadata(
            n_pixels=n_pixels,
            dead=dead,
        )
        writer.write_mapping(mapping)


def main():
    file = Lab_Window()
    output_path = get_data("time_corrections/time_corrections_lab.h5")
    process(file, output_path)

    file = MCLab_Opct40_Window_5MHz()
    output_path = get_data("time_corrections/time_corrections_mc.h5")
    process(file, output_path)

    file = CHECM()
    output_path = get_data("time_corrections/time_corrections_checm.h5")
    process(file, output_path)


if __name__ == '__main__':
    main()
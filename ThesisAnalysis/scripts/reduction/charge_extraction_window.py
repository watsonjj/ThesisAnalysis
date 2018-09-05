from ThesisAnalysis import get_data, ThesisHDF5Writer
from CHECLabPy.core.io_simtel import ReaderSimtel
from CHECLabPy.waveform_reducers.average_wf import AverageWF
from CHECLabPy.utils.waveform import BaselineSubtractor
import numpy as np
import pandas as pd
from tqdm import tqdm


poi = 888
t_event = 46
sizes = np.arange(1, 50)
shifts = np.arange(-40, 25)


def process(input_path, output_path, plot_event=None):
    reader = ReaderSimtel(input_path, max_events=1000)
    n_events = reader.n_events
    n_samples = reader.n_samples

    baseline_subtractor = BaselineSubtractor(reader)
    waveform_array = np.zeros((n_events, n_samples))
    true_array = np.zeros(n_events)
    for iev, wf in enumerate(reader):
        wf = baseline_subtractor.subtract(wf)
        waveform_array[iev] = wf[poi]
        true_array[iev] = reader.mc_true[poi]

    if plot_event is not None:
        df_wf = pd.DataFrame(dict(wf=waveform_array[plot_event]))
        wf_path = get_data("charge_extraction_window/wf.h5")
        with ThesisHDF5Writer(wf_path) as writer:
            writer.write(data=df_wf)

    d_list = []

    for size in tqdm(sizes, desc="Size"):
        for shift in tqdm(shifts, desc="Shift"):
            reducer = AverageWF(n_events, n_samples,
                                extract_charge_only=True, t_event=t_event,
                                window_size=size, window_shift=shift)
            noise_reducer = AverageWF(n_events, n_samples,
                                      extract_charge_only=True, t_event=0,
                                      window_size=size, window_shift=0)

            charge = reducer.process(waveform_array)['charge']
            noise = noise_reducer.process(waveform_array)['charge']

            snr = np.mean(charge) / np.std(noise)

            d_list.append(dict(
                size=size,
                shift=shift,
                snr=snr,
            ))

    df = pd.DataFrame(d_list)
    with ThesisHDF5Writer(output_path) as writer:
        writer.write(data=df)


def main():
    input_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/5mhz/run43515.simtel.gz"
    output_path = get_data("charge_extraction_window/amp1nsb5.h5")
    process(input_path, output_path)

    input_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/5mhz/run43495.simtel.gz"
    output_path = get_data("charge_extraction_window/amp50nsb5.h5")
    process(input_path, output_path)

    input_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/125mhz/run43515.simtel.gz"
    output_path = get_data("charge_extraction_window/amp1nsb125.h5")
    process(input_path, output_path)

    input_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/125mhz/run43495.simtel.gz"
    output_path = get_data("charge_extraction_window/amp50nsb125.h5")
    process(input_path, output_path, 53)


if __name__ == '__main__':
    main()

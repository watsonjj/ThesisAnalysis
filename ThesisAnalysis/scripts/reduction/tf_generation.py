from ThesisAnalysis import get_data, ThesisHDF5Writer
import numpy as np
import pandas as pd
from CHECLabPy.core.io import TIOReader
from tqdm import tqdm
from glob import glob
from CHECLabPy.utils.waveform import shift_waveform
import re


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split('(\d+)', text) ]


def process(files, output_path, t_shift, checm=False):

    files.sort(key=natural_keys)

    df_list = []

    potential_saturation = False

    for ifile, f in enumerate(files):
        reader = TIOReader(f, max_events=1000)

        n_events = reader.n_events
        n_samples = reader.n_samples

        average_wf = np.zeros((n_events, n_samples))

        desc = "Processing events"
        n = 0
        for wf in tqdm(reader, total=n_events, desc=desc):
            iev = reader.index
            if t_shift:
                wf = shift_waveform(wf, t_shift)
            average_wf[iev] = wf[0]

        if checm:
            if average_wf.max() > 2000:
                potential_saturation = True

        if potential_saturation:
            average_wf = np.ma.masked_where(average_wf < 10, average_wf)

        df_list.append(pd.DataFrame(dict(
            ifile=ifile,
            file=f,
            wf=average_wf.mean(0),
            isam=np.arange(n_samples)
        )))

    df = pd.concat(df_list, ignore_index=True)

    with ThesisHDF5Writer(output_path) as writer:
        writer.write(data=df)
        writer.write_metadata(n_files=len(files))


def main():
    files = glob("/Volumes/gct-jason/thesis_data/checm/tf/*_r1.tio")
    output_path = get_data("tf/t5_input.h5")
    process(files, output_path, None, True)

    files = glob("/Volumes/gct-jason/thesis_data/checs/lab/tf/*_r1.tio")
    output_path = get_data("tf/tc_input.h5")
    process(files, output_path, 43)


if __name__ == '__main__':
    main()

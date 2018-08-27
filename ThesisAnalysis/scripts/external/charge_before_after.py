from ThesisAnalysis import ThesisHDF5Writer, ThesisHDF5Reader
from ThesisAnalysis.files import all_files
import pandas as pd


def process(file):
    charge_averages_path = file.charge_averages_path
    illumination_path = file.illumination_profile_path
    fw_path = file.fw_path
    ff_path = file.ff_path
    charge_before_after_path = file.charge_before_after_path

    with ThesisHDF5Reader(charge_averages_path) as reader:
        df = reader.read("data")

    with ThesisHDF5Reader(fw_path) as reader:
        fw_m = reader.read("data")['fw_m'].values

    with ThesisHDF5Reader(ff_path) as reader:
        df_ff = reader.read("data")
        ff_m = df_ff['ff_m'].values
        gamma_q = ff_m.mean(),
        gamma_ff = ff_m.mean()/ff_m

    with ThesisHDF5Reader(illumination_path) as reader:
        correction = reader.read("correction")['correction'].values

    pixel = df['pixel'].values
    fw_pos = df['fw_pos'].values
    transmission = df['transmission'].values
    runlist_expected = df['pe_expected'].values
    camera_expected = transmission * (fw_m / correction)[0]
    pixel_expected = transmission * fw_m[pixel]
    before_mVns = df['mean']
    before_mVns_std = df['std']
    before_mVns_ip = df['mean'] / correction[pixel]
    before_mVns_ip_std = df['std'] / correction[pixel]
    before = df['mean'] / gamma_q
    before_std = df['std'] / gamma_q
    before_ip = before / correction[pixel]
    before_ip_std = before_std / correction[pixel]
    after = df['mean'] * gamma_ff[pixel] / gamma_q
    after_std = df['std'] * gamma_ff[pixel] / gamma_q
    after_ip = after / correction[pixel]
    after_ip_std = after_std / correction[pixel]

    df_new = pd.DataFrame(dict(
        run_number=df['run_number'],
        fw_pos=fw_pos,
        transmission=transmission,
        runlist_expected=runlist_expected,
        pixel=df['pixel'],
        camera_expected=camera_expected,
        pixel_expected=pixel_expected,
        before_mVns=before_mVns,
        before_mVns_std=before_mVns_std,
        before_mVns_ip=before_mVns_ip,
        before_mVns_ip_std=before_mVns_ip_std,
        before=before,
        before_std=before_std,
        before_ip=before_ip,
        before_ip_std=before_ip_std,
        after=after,
        after_std=after_std,
        after_ip=after_ip,
        after_ip_std=after_ip_std,
    ))

    with ThesisHDF5Writer(charge_before_after_path) as writer:
        writer.write(data=df_new)


def main():
    [process(f) for f in all_files]


if __name__ == '__main__':
    main()

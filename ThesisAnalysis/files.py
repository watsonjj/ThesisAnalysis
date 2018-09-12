from ThesisAnalysis import get_data, ThesisHDF5Reader
from abc import abstractmethod, ABCMeta
import os
from CHECLabPy.utils.files import open_runlist_dl1, open_runlist_r1
from glob import glob
from CHECLabPy.core.io import DL1Reader
import numpy as np


class File(metaclass=ABCMeta):
    def __init__(self, **kwargs):
        self.poi = 888
        self.dead = []
        self.illumination_profile_path = None
        self.fw_path = None
        self.ff_path = None
        self.runlist_path = None
        self.spe_path = None
        self.spe_config_path = None

    @property
    def spe_runlist_path(self):
        return self.runlist_path

    @property
    def charge_averages_path(self):
        return os.path.join(os.path.dirname(self.runlist_path), "charge_averages.h5")

    @property
    def charge_resolution_path(self):
        return os.path.join(os.path.dirname(self.runlist_path), "charge_resolution.h5")

    @property
    def charge_before_after_path(self):
        return os.path.join(os.path.dirname(self.runlist_path), "charge_before_after.h5")

    @property
    def spe_files(self):
        df = open_runlist_dl1(self.runlist_path, open_readers=False)
        path_list = df.iloc[-7:-4]['path'].tolist()
        return path_list

    @property
    def reader_list(self):
        return open_runlist_dl1(self.runlist_path)['reader'].tolist()

    @abstractmethod
    def is_abstract(self):
        return True

    def get_dataframe(self, r1=False, open_readers=True):
        if r1:
            df = open_runlist_r1(self.runlist_path, open_readers)
        else:
            df = open_runlist_dl1(self.runlist_path, open_readers)
        df['transmission'] = 1/df['fw_atten']

        with ThesisHDF5Reader(self.fw_path) as reader:
            fw_m = reader.read_metadata()['fw_m_camera']
            fw_merr = reader.read_metadata()['fw_merr_camera']

        df['expected'] = df['transmission'] * fw_m
        df['expected_err'] = df['transmission'] * fw_merr
        return df

    def get_run_with_illumination(self, illumination, r1=False):
        df = self.get_dataframe(r1=r1, open_readers=False)
        idxmin = np.abs(df['expected'] - illumination).idxmin()
        expected = df.loc[idxmin]['expected']
        epected_err = df.loc[idxmin]['expected_err']
        print("Run at illumination {:.3f} ± {:.3f} p.e. obtained".format(expected, epected_err))
        path = df.loc[idxmin]['path']
        return path, expected, epected_err


class MC(File):
    def __init__(self, mc_true=False, **kwargs):
        super().__init__(**kwargs)
        self.mc_true = mc_true
        self.illumination_profile_path = get_data("mc_illumination_profile_correction.h5")

    @property
    def charge_resolution_mc_path(self):
        return os.path.join(os.path.dirname(self.runlist_path), "charge_resolution_mc.h5")

    @property
    def charge_resolution_path(self):
        if self.mc_true:
            return self.charge_resolution_mc_path
        else:
            return super().charge_resolution_path


class MCLab(MC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.illumination_profile_path = get_data("mc_illumination_profile_correction.h5")


class MCLab_Opct40(MCLab):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fw_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/5mhz/fw_calibration.h5"
        self.ff_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/5mhz/ff_coefficients.h5"
        self.mc_calib_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/5mhz/mc_calib.h5"


class MCLab_Opct40_0MHz(MCLab_Opct40):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.runlist_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/0mhz/runlist.txt"
        self.spe_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/0mhz/spe.h5"

    def is_abstract(self):
        return False


class MCLab_Opct40_5MHz(MCLab_Opct40):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.runlist_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/5mhz/runlist.txt"
        self.spe_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/5mhz/spe.h5"
        self.spe_config_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/5mhz/config.yml"

    def is_abstract(self):
        return False

class MCLab_Opct40_40MHz(MCLab_Opct40):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.runlist_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/40mhz/runlist.txt"
        self.spe_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/40mhz/spe.h5"

    def is_abstract(self):
        return False


class MCLab_Opct40_125MHz(MCLab_Opct40):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.runlist_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/125mhz/runlist.txt"
        self.spe_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/125mhz/spe.h5"

    def is_abstract(self):
        return False


class MCLab_Opct40_1200MHz(MCLab_Opct40):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.runlist_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/1200mhz/runlist.txt"
        self.spe_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/1200mhz/spe.h5"

    def is_abstract(self):
        return False


class MCLab_Opct40_Window(MCLab):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fw_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/window_extractor/5mhz/fw_calibration.h5"
        self.ff_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/window_extractor/5mhz/ff_coefficients.h5"
        self.mc_calib_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/window_extractor/5mhz/mc_calib.h5"


class MCLab_Opct40_Window_5MHz(MCLab_Opct40_Window):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.runlist_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/window_extractor/5mhz/runlist.txt"
        self.spe_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/window_extractor/5mhz/spe.h5"
        self.spe_config_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/4_opct40/window_extractor/5mhz/config.yml"

    def is_abstract(self):
        return False


class MCLab_Opct40_Window_125MHz(MCLab_Opct40_Window):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.runlist_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/3_opct40/window_extractor/125mhz/runlist.txt"

    def is_abstract(self):
        return False


class MCLab_Opct20_Window(MCLab):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fw_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/4_opct20/window_extractor/5mhz/fw_calibration.h5"
        self.ff_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/4_opct20/window_extractor/5mhz/ff_coefficients.h5"
        self.mc_calib_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/4_opct20/window_extractor/5mhz/mc_calib.h5"


class MCLab_Opct20_Window_5MHz(MCLab_Opct20_Window):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.runlist_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/4_opct20/window_extractor/5mhz/runlist.txt"
        self.spe_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/4_opct20/window_extractor/5mhz/spe.h5"
        self.spe_config_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/4_opct20/window_extractor/5mhz/config.yml"

    def is_abstract(self):
        return False


class MCLab_Opct20_Window_125MHz(MCLab_Opct20_Window):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.runlist_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/4_opct20/window_extractor/125mhz/runlist.txt"

    def is_abstract(self):
        return False


class MCLab_Opct20_Window_5MHz_HEN(MCLab_Opct20_Window):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.runlist_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/5_highnoise/opct20/window/runlist.txt"
        self.spe_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/5_highnoise/opct20/window/spe.h5"

    def is_abstract(self):
        return False


class MCLab_Opct20(MCLab):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fw_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/4_opct20/5mhz/fw_calibration.h5"
        self.ff_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/4_opct20/5mhz/ff_coefficients.h5"
        self.mc_calib_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/4_opct20/5mhz/mc_calib.h5"


class MCLab_Opct20_5MHz(MCLab_Opct20):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.runlist_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/4_opct20/5mhz/runlist.txt"
        self.spe_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/4_opct20/5mhz/spe.h5"
        self.spe_config_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/4_opct20/5mhz/config.yml"

    def is_abstract(self):
        return False


class MCLab_Opct20_125MHz(MCLab_Opct20):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.runlist_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/4_opct20/125mhz/runlist.txt"
        self.spe_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/4_opct20/125mhz/spe.h5"

    def is_abstract(self):
        return False


class MCLab_Opct20_CC_5MHz_HEN(MCLab_Opct20):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.runlist_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/5_highnoise/opct20/cc/runlist.txt"
        self.spe_path = "/Volumes/gct-jason/thesis_data/checs/mc/dynrange/5_highnoise/opct20/cc/spe.h5"

    def is_abstract(self):
        return False


class MCOnSky(MC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.glob_path = None

    @property
    def reader_list(self):
        readers = [DL1Reader(fp) for fp in glob(self.glob_path)]
        return readers

    @property
    def charge_resolution_mc_path(self):
        first_file = glob(self.glob_path)[0]
        return os.path.join(os.path.dirname(first_file), "charge_resolution_mc.h5")


class MCOnSky_5MHz(MCOnSky):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class MCOnSky_5MHz_CC_Local(MCOnSky_5MHz):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.glob_path = "/Volumes/gct-jason/thesis_data/checs/mc/onsky/gamma/5mhz/cc_local/*_dl1.h5"
        self.mc_calib_path = "/Volumes/gct-jason/thesis_data/checs/mc/onsky/gamma/5mhz/cc_local/mc_calib.h5"

    def is_abstract(self):
        return False


class MCOnSky_5MHz_CC_Neighbour(MCOnSky_5MHz):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.glob_path = "/Volumes/gct-jason/thesis_data/checs/mc/onsky/gamma/5mhz/cc_neighbour/*_dl1.h5"
        self.mc_calib_path = "/Volumes/gct-jason/thesis_data/checs/mc/onsky/gamma/5mhz/cc_local/mc_calib.h5"

    def is_abstract(self):
        return False


class MCOnSky_5MHz_Window_Local(MCOnSky_5MHz):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.glob_path = "/Volumes/gct-jason/thesis_data/checs/mc/onsky/gamma/5mhz/window_local/*_dl1.h5"
        self.mc_calib_path = "/Volumes/gct-jason/thesis_data/checs/mc/onsky/gamma/5mhz/window_local/mc_calib.h5"


    def is_abstract(self):
        return False


class MCOnSky_5MHz_Window_Neighbour(MCOnSky_5MHz):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.glob_path = "/Volumes/gct-jason/thesis_data/checs/mc/onsky/gamma/5mhz/window_neighbour/*_dl1.h5"
        self.mc_calib_path = "/Volumes/gct-jason/thesis_data/checs/mc/onsky/gamma/5mhz/window_local/mc_calib.h5"

    def is_abstract(self):
        return False


class MCOnSky_125MHz(MCOnSky):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class MCOnSky_125MHz_CC_Local(MCOnSky_125MHz):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.glob_path = "/Volumes/gct-jason/thesis_data/checs/mc/onsky/gamma/125mhz/cc_local/*_dl1.h5"
        self.mc_calib_path = "/Volumes/gct-jason/thesis_data/checs/mc/onsky/gamma/5mhz/cc_local/mc_calib.h5"

    def is_abstract(self):
        return False


class MCOnSky_125MHz_CC_Neighbour(MCOnSky_125MHz):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.glob_path = "/Volumes/gct-jason/thesis_data/checs/mc/onsky/gamma/125mhz/cc_neighbour/*_dl1.h5"
        self.mc_calib_path = "/Volumes/gct-jason/thesis_data/checs/mc/onsky/gamma/5mhz/cc_local/mc_calib.h5"

    def is_abstract(self):
        return False


class MCOnSky_125MHz_Window_Local(MCOnSky_125MHz):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.glob_path = "/Volumes/gct-jason/thesis_data/checs/mc/onsky/gamma/125mhz/window_local/*_dl1.h5"
        self.mc_calib_path = "/Volumes/gct-jason/thesis_data/checs/mc/onsky/gamma/5mhz/window_local/mc_calib.h5"

    def is_abstract(self):
        return False


class MCOnSky_125MHz_Window_Neighbour(MCOnSky_125MHz):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.glob_path = "/Volumes/gct-jason/thesis_data/checs/mc/onsky/gamma/125mhz/window_neighbour/*_dl1.h5"
        self.mc_calib_path = "/Volumes/gct-jason/thesis_data/checs/mc/onsky/gamma/5mhz/window_local/mc_calib.h5"

    def is_abstract(self):
        return False


class Lab(File):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.illumination_profile_path = get_data("mc_illumination_profile_correction.h5")  # TODO: get lab_illumination_profile_correction.h5
        self.dead = [677, 293, 27, 1925, 1955]


class Lab_TFNone(Lab):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fw_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_none/fw_calibration.h5"
        self.ff_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_none/ff_coefficients.h5"
        self.runlist_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_none/runlist.txt"
        self.spe_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_none/spe.h5"
        self.spe_config_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_none/config.yml"

    def is_abstract(self):
        return False


class Lab_TFPchip(Lab):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fw_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_pchip/fw_calibration.h5"
        self.ff_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_pchip/ff_coefficients.h5"
        self.runlist_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_pchip/runlist.txt"
        self.spe_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_pchip/spe.h5"

    def is_abstract(self):
        return False


class Lab_TFPoly(Lab):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fw_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_poly/fw_calibration.h5"
        self.ff_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_poly/ff_coefficients.h5"
        self.runlist_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_poly/runlist.txt"
        self.spe_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_poly/spe.h5"

    def is_abstract(self):
        return False


class Lab_TFWithPed(Lab):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fw_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_withped/fw_calibration.h5"
        self.ff_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_withped/ff_coefficients.h5"
        self.runlist_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_withped/runlist.txt"
        self.spe_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/tf/tf_withped/spe.h5"

    def is_abstract(self):
        return False


class Lab_GM50ADC(Lab):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fw_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/gain/tf_poly/50ADC/fw_calibration.h5"
        self.ff_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/gain/tf_poly/50ADC/ff_coefficients.h5"
        self.runlist_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/gain/tf_poly/50ADC/runlist.txt"
        self.spe_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/gain/tf_poly/50ADC/spe.h5"
        self.spe_config_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/gain/tf_poly/50ADC/config.yml"

    def is_abstract(self):
        return False


class Lab_GM100ADC(Lab):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fw_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/gain/tf_poly/100ADC/fw_calibration.h5"
        self.ff_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/gain/tf_poly/100ADC/ff_coefficients.h5"
        self.runlist_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/gain/tf_poly/100ADC/runlist.txt"
        self.spe_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/gain/tf_poly/100ADC/spe.h5"

    def is_abstract(self):
        return False


class Lab_GM200ADC(Lab):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fw_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/gain/tf_poly/200ADC/fw_calibration.h5"
        self.ff_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/gain/tf_poly/200ADC/ff_coefficients.h5"
        self.runlist_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/gain/tf_poly/200ADC/runlist.txt"
        self.spe_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/gain/tf_poly/200ADC/spe.h5"

    def is_abstract(self):
        return False


class Lab_Window(Lab):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fw_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/window_extractor/fw_calibration.h5"
        self.ff_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/window_extractor/ff_coefficients.h5"
        self.runlist_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/window_extractor/runlist.txt"
        self.spe_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/window_extractor/spe.h5"

    def is_abstract(self):
        return False


class Lab_GM50ADC_Original(Lab):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fw_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/gain/tf_poly/50ADC/original/fw_calibration.h5"
        self.ff_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/gain/tf_poly/50ADC/original/ff_coefficients.h5"
        self.runlist_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/gain/tf_poly/50ADC/original/runlist.txt"
        self.spe_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/gain/tf_poly/50ADC/spe.h5"

    def is_abstract(self):
        return False


class Lab_GM100ADC_Original(Lab):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fw_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/gain/tf_poly/100ADC/original/fw_calibration.h5"
        self.ff_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/gain/tf_poly/100ADC/original/ff_coefficients.h5"
        self.runlist_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/gain/tf_poly/100ADC/original/runlist.txt"
        self.spe_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/gain/tf_poly/100ADC/spe.h5"

    def is_abstract(self):
        return False


class Lab_GM200ADC_Original(Lab):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fw_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/gain/tf_poly/200ADC/original/fw_calibration.h5"
        self.ff_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/gain/tf_poly/200ADC/original/ff_coefficients.h5"
        self.runlist_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/gain/tf_poly/200ADC/original/runlist.txt"
        self.spe_path = "/Volumes/gct-jason/thesis_data/checs/lab/dynrange/gain/tf_poly/200ADC/spe.h5"

    def is_abstract(self):
        return False


class CHECM(File):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.illumination_profile_path = get_data("mc_illumination_profile_correction.h5")  # TODO: get lab_illumination_profile_correction.h5
        self.dead = [96, 276, 1906, 1910, 1916]
        self.fw_path = "/Volumes/gct-jason/thesis_data/checm/dynrange/selected/fw_calibration.h5"
        self.ff_path = "/Volumes/gct-jason/thesis_data/checm/dynrange/selected/ff_coefficients.h5"
        self.runlist_path = "/Volumes/gct-jason/thesis_data/checm/dynrange/selected/runlist.txt"
        self.spe_path = "/Volumes/gct-jason/thesis_data/checm/spe/spe.h5"

    @property
    def spe_runlist_path(self):
        return "/Volumes/gct-jason/thesis_data/checm/spe/runlist.txt"

    @property
    def spe_files(self):
        path_list = [
            "/Volumes/gct-jason/thesis_data/checm/spe/Run00071_dl1.h5",
            "/Volumes/gct-jason/thesis_data/checm/spe/Run00072_dl1.h5",
            "/Volumes/gct-jason/thesis_data/checm/spe/Run00073_dl1.h5"
        ]
        return path_list

    def is_abstract(self):
        return False


all_files = [
    MCLab_Opct40_0MHz(),
    MCLab_Opct40_5MHz(),
    MCLab_Opct40_40MHz(),
    MCLab_Opct40_125MHz(),
    MCLab_Opct40_1200MHz(),
    MCLab_Opct20_5MHz(),
    MCLab_Opct20_125MHz(),
    MCLab_Opct40_Window_5MHz(),
    MCLab_Opct40_Window_125MHz(),
    MCLab_Opct20_Window_5MHz(),
    MCLab_Opct20_Window_125MHz(),
    MCLab_Opct20_Window_5MHz_HEN(),
    MCLab_Opct20_CC_5MHz_HEN(),
    Lab_TFNone(),
    Lab_TFPchip(),
    Lab_TFPoly(),
    Lab_TFWithPed(),
    Lab_GM50ADC(),
    Lab_GM100ADC(),
    Lab_GM200ADC(),
    Lab_Window(),
    CHECM(),
]

fw_correction_original_files = [
    Lab_GM50ADC_Original(),
    Lab_GM100ADC_Original(),
    Lab_GM200ADC_Original(),
]
fw_correction_post_files = [
    Lab_GM50ADC(),
    Lab_GM100ADC(),
    Lab_GM200ADC(),
]

calib_files = [
    MCLab_Opct40_5MHz(),
    MCLab_Opct20_5MHz(),
    MCLab_Opct40_Window_5MHz(),
    MCLab_Opct20_Window_5MHz(),
    Lab_TFNone(),
    Lab_TFPchip(),
    Lab_TFPoly(),
    Lab_TFWithPed(),
    Lab_GM50ADC(),
    Lab_GM100ADC(),
    Lab_GM200ADC(),
    Lab_Window(),
    CHECM(),
]

spe_files = [
    MCLab_Opct40_5MHz(),
    MCLab_Opct20_5MHz(),
    Lab_TFNone(),
    Lab_TFPchip(),
    Lab_TFPoly(),
    Lab_TFWithPed(),
    Lab_GM50ADC(),
    Lab_GM100ADC(),
    Lab_GM200ADC(),
]

mc_calib_files = [
    MCLab_Opct40_5MHz(),
    MCLab_Opct20_5MHz(),
    MCLab_Opct40_Window_5MHz(),
    MCLab_Opct20_Window_5MHz(),
]

mc_onsky_calib_files = [
    MCOnSky_5MHz_CC_Local(),
    MCOnSky_5MHz_Window_Local(),
]

mc_files = [
    MCLab_Opct40_0MHz(),
    MCLab_Opct40_5MHz(),
    MCLab_Opct40_40MHz(),
    MCLab_Opct40_125MHz(),
    MCLab_Opct40_1200MHz(),
    MCLab_Opct20_5MHz(),
    MCLab_Opct20_125MHz(),
    MCLab_Opct40_Window_5MHz(),
    MCLab_Opct40_Window_125MHz(),
    MCLab_Opct20_Window_5MHz(),
    MCLab_Opct20_Window_125MHz(),
    MCLab_Opct20_Window_5MHz_HEN(),
    MCLab_Opct20_CC_5MHz_HEN(),
    MCOnSky_5MHz_CC_Local(),
    MCOnSky_5MHz_CC_Neighbour(),
    MCOnSky_5MHz_Window_Local(),
    MCOnSky_5MHz_Window_Neighbour(),
    MCOnSky_125MHz_CC_Local(),
    MCOnSky_125MHz_CC_Neighbour(),
    MCOnSky_125MHz_Window_Local(),
    MCOnSky_125MHz_Window_Neighbour(),
]
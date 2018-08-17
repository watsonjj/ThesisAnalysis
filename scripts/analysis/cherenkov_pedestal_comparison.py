from ThesisAnalysis.plotting.camera import CameraImage
from ThesisAnalysis import get_data, get_plot, ThesisHDF5Reader
import warnings


def main():
    path = get_data("cherenkov_pedestal_comparison.h5")
    with ThesisHDF5Reader(path) as reader:
        df = reader.read("data")
        mapping = reader.read_mapping()

    mapping_mirror = mapping.copy()
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', UserWarning)
        mapping_mirror.metadata = mapping.metadata
    mapping_mirror['xpix'] = -mapping_mirror['xpix']
    mapping_mirror['ypix'] = -mapping_mirror['ypix']

    p_r0 = CameraImage.from_mapping(mapping_mirror, switch_backend=True)
    p_r0.image = df['r0'].values
    p_r0.add_colorbar("Raw Integration (ADC ns)")
    p_r0.save(get_plot("pedestal/r0_cherenkov_image_mirrored.pdf"))

    p_r1 = CameraImage.from_mapping(mapping, switch_backend=True)
    p_r1.image = df['r1'].values
    p_r1.add_colorbar("Pedestal-Subtracted Integration (ADC ns)")
    p_r1.save(get_plot("pedestal/r1_cherenkov_image_mirrored.pdf"))

    p_r1pe = CameraImage.from_mapping(mapping, switch_backend=True)
    p_r1pe.image = df['r1pe'].values
    p_r1pe.add_colorbar("Calibrated Integration (p.e.)")
    p_r1pe.save(get_plot("pedestal/r1pe_cherenkov_image_mirrored.pdf"))


if __name__ == '__main__':
    main()

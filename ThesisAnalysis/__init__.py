import os
import pandas as pd
import warnings

_ROOT = os.path.abspath(os.path.dirname(__file__))


def get_data(path):
    return os.path.join(_ROOT, 'data', path)


def get_plot(path):
    return os.path.join(_ROOT, 'plots', path)

def get_thesis_figure(chapter, file):
    d = "/Users/Jason/Dropbox/DropboxDocuments/University/Oxford/Reports/Thesis/figures"
    path = os.path.join(d, chapter, file)
    return path


class ThesisHDF5Writer:
    def __init__(self, path):
        self.path = path
        output_dir = os.path.dirname(path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print("Created directory: {}".format(output_dir))

        self.store = pd.HDFStore(
            path, mode='w', complevel=9, complib='blosc:blosclz'
        )
        print("HDF5 Created: {}".format(self.path))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.store.close()

    def write(self, **kwargs):
        for key, value in kwargs.items():
            self.store[key] = value

    def write_mapping(self, mapping):
        self.store['mapping'] = mapping
        mapping_meta = mapping.metadata
        self.store.get_storer('mapping').attrs.metadata = mapping_meta

    def write_metadata(self, **metadata):
        self.store['metadata'] = pd.DataFrame()
        self.store.get_storer('metadata').attrs.metadata = metadata


class ThesisHDF5Reader:
    def __init__(self, path):
        self.path = path

        self.store = pd.HDFStore(
            path, mode='r', complevel=9, complib='blosc:blosclz'
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.store.close()

    def read(self, table):
        return self.store[table]

    def read_mapping(self):
        mapping = self.store['mapping']
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)
            mapping.metadata = self.store.get_storer('mapping').attrs.metadata
        return mapping

    def read_metadata(self):
        metadata = self.store.get_storer('metadata').attrs.metadata
        return metadata

# def create_h5(path, mapping=None, metadata=None, **kwargs):
#     output_dir = os.path.dirname(path)
#     if not os.path.exists(output_dir):
#         os.makedirs(output_dir)
#         print("Created directory: {}".format(output_dir))
#
#     with pd.HDFStore(path, 'w') as store:
#         for key, value in kwargs.items():
#             store[key] = value
#
#         if mapping is not None:
#             store['mapping'] = mapping
#             mapping_meta = mapping.metadata
#             store.get_storer('mapping').attrs.metadata = mapping_meta
#
#         if metadata is not None:
#             store['metadata'] = pd.DataFrame()
#             store.get_storer('metadata').attrs.metadata = metadata
#
#     print("Data saved to: {}".format(path))

import matplotlib as mpl
mpl.use('pgf')
import os
from CHECLabPy.plotting.setup import Plotter

class ThesisPlotter(Plotter):
    def __init__(self, ax=None):
        super().__init__(ax)

        # rc = {
        #     "font.family": [u"Helvetica"],
        #     "xtick.labelsize": 10,
        #     "ytick.labelsize": 10,
        #     "font.size": 10,
        #     "axes.titlesize": 10,
        #     "axes.labelsize": 10,
        #     "legend.fontsize": 8,
        #     "lines.markeredgewidth": 1
        # }

        rc = {  # setup matplotlib to use latex for output
            "pgf.texsystem": "pdflatex", # change this if using xetex or lautex
            "text.usetex": True,         # use LaTeX to write all text
            "font.family": "cursive",
            "font.serif": [],            # blank entries should cause plots to inherit fonts from the document
            "font.sans-serif": [],
            "font.monospace": [],
            "font.cursive": [],
            "font.size": 10,
            "axes.titlesize": 10,
            "axes.labelsize": 10,        # LaTeX default is 10pt font.
            "legend.fontsize": 8,        # Make the legend/label fonts a little smaller
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "figure.figsize": self.figsize(0.9), # default fig size of 0.9 textwidth
            "lines.markeredgewidth": 1,
            "pgf.preamble": [
                r"\usepackage[utf8x]{inputenc}", # use utf8 fonts becasue your computer can handle it :)
                r"\usepackage[T1]{fontenc}" # plots will be generated using this preamble
            ]
        }

        mpl.rcParams.update(rc)

    def create_figure(self):
        fig, ax = super().create_figure()

        fmt = mpl.ticker.StrMethodFormatter("{x}")
        ax.xaxis.set_major_formatter(fmt)
        ax.yaxis.set_major_formatter(fmt)
        return fig, ax

    def save(self, output_name):
        directory = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(directory, output_name)
        path_pdf = path + ".pdf"
        path_pgf = path + ".pgf"
        super().save(path_pdf)
        # self.fig.savefig(path_pgf, bbox_inches='tight')
        # print("Figure saved to: {}".format(path_pgf))

from ThesisAnalysis import get_data, ThesisHDF5Reader, ThesisHDF5Writer
from ThesisAnalysis.files import Lab_TFPoly
from ThesisAnalysis.plotting.resolutions import ChargeResolutionWRRPlotter
import numpy as np
import pandas as pd
import iminuit
from IPython import embed
from scipy.stats import poisson


def sigma_0(nsb, window_size, electronic_noise):
    # Convert from MHz to pe/ns
    nsb /= 1000
    return np.sqrt(nsb * window_size + electronic_noise ** 2)


class Fitter:
    def __init__(self):
        self.p0 = dict(
            sigma_0=sigma_0(0.125, 15, 0.87),
            enf=0.25,
            miscal=0.1,
        )
        self.limits = dict(
            limit_sigma_0=(0, 3),
            limit_enf=(0.1, 1),
            limit_miscal=(0, 0.5),
        )
        self.fix = dict(
        )

    @staticmethod
    def charge_resolution(q, sigma_0=sigma_0(0.125, 15, 0.87), enf=0.2, miscal=0.1):
        return np.sqrt(
            sigma_0 ** 2 +
            (1 + enf) ** 2 * q +
            (miscal * q) ** 2
        ) / q

    def fit(self, x, y):
        yreq = self.charge_resolution(x)

        def minimize(sigma_0, enf, miscal):
            p = self.charge_resolution(
                x, sigma_0, enf, miscal
            )
            like = -2 * poisson._logpmf(y / yreq, p / yreq)
            return np.sum(like ** 2)

        m0 = iminuit.Minuit(minimize, **self.p0, **self.limits, **self.fix,
                            print_level=0, pedantic=False, throw_nan=True)
        m0.migrad()
        coeff = m0.values
        m0.hesse()
        errors = m0.errors

        return coeff, errors


# class FitPlotter(ChargeResolutionWRRPlotter):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.fitter = Fitter()
#
#     def set_df(self, df):
#         self.df_pixel = df
#
#     def plot_fit(self):
#         df =
#         x = self.df_pixel['true'].values
#         y = self.df_pixel['charge_resolution'].values
#         coeff, errors = self.fitter.fit(x, y)
#
#         for c in coeff.keys():
#             print(c, "{:#.3f} \pm {:#.3f}".format(coeff[c], errors[c]))
#
#         yreq = Fitter.charge_resolution(x)
#         # self.ax.plot(x, self.fitter.charge_resolution(x, **coeff)/yreq,
#         #              '--', color='red', label='Fit')


def process(file, output_path):
    path = file.charge_resolution_path
    dead = file.dead

    with ThesisHDF5Reader(path) as reader:
        df = reader.read('charge_resolution_pixel')
        df = df.loc[df['true'] < 300]
        df = df.loc[~df['pixel'].isin(dead)]

    fitter = Fitter()

    x = df['true'].values
    y = df['charge_resolution'].values
    coeff, errors = fitter.fit(x, y)

    for c in coeff.keys():
        print(c, "{:#.3g} \pm {:#.3g}".format(coeff[c], errors[c]))

    xf = np.geomspace(0.1, 1000, 100)
    yf = fitter.charge_resolution(xf, **coeff)

    coeff['sigma_0'] = sigma_0(125, 15, 0.3)
    ynsb = fitter.charge_resolution(xf, **coeff)

    enf = coeff['enf']
    opct = 0.1
    coeff['enf'] = opct
    yopct_geo = fitter.charge_resolution(xf, **coeff)
    coeff['enf'] = opct + (3/2) * opct ** 2
    yopct_branching = fitter.charge_resolution(xf, **coeff)

    df = pd.DataFrame(dict(
        x=xf,
        y=yf,
        ynsb=ynsb,
        yopct_geo=yopct_geo,
        yopct_branching=yopct_branching,
    ))

    with ThesisHDF5Writer(output_path) as writer:
        writer.write(data=df)


def main():
    file = Lab_TFPoly()
    output_path = get_data("charge_res_fit.h5")
    process(file, output_path)


if __name__ == '__main__':
    main()

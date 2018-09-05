''''
Plot the laser and curved FP correction factors
'''

import sys
import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.ticker import AutoMinorLocator
from scipy import ndimage
import argparse
from scipy.interpolate import spline
from scipy import optimize
import scipy as sp
import pandas as pd

def LoadCorrection(file="total_correction.txt"):
    data = np.loadtxt(file, dtype=float, skiprows=1)
    pix = data[:,0]
    flat = data[:, 1]
    laser = data[:, 2]
    total = data[:, 3]
    return  pix, flat, laser, total

def DrawPixel(x,y,dx=6e-3,dy=6e-3,col='black',lw=1.0):
    plt.plot([x - dx / 2.0, x - dx / 2.0], [y - dy / 2.0, y + dy / 2.0], 'k-', color=col, lw=lw)
    plt.plot([x + dx / 2.0, x + dx / 2.0], [y - dy / 2.0, y + dy / 2.0], 'k-', color=col, lw=lw)
    plt.plot([x - dx / 2.0, x + dx / 2.0], [y - dy / 2.0, y - dy / 2.0], 'k-', color=col, lw=lw)
    plt.plot([x - dx / 2.0, x + dx / 2.0], [y + dy / 2.0, y + dy / 2.0], 'k-', color=col, lw=lw)

def DrawPixels(x, y):
    for i in range(len(x)):
        DrawPixel(x[i], y[i])

def DrawBox():
    bb = -0.20
    bt = +0.18
    bl = -0.19
    br = +0.18
    plt.plot([bl, bl], [bb, bt], 'k-', lw=1)
    plt.plot([br, br], [bb, bt], 'k-', lw=1)
    plt.plot([bl, br], [bb, bb], 'k-', lw=1)
    plt.plot([bl, br], [bt, bt], 'k-', lw=1)

def DrawCameraOutline():
    ms = (51.4 + 2) / 1000.0
    plt.plot([-3 * ms, -3 * ms], [-2 * ms, +2 * ms], 'k-', lw=2)
    plt.plot([+3 * ms, +3 * ms], [-2 * ms, +2 * ms], 'k-', lw=2)
    plt.plot([-2 * ms, -2 * ms], [-3 * ms, -2 * ms], 'k-', lw=2)
    plt.plot([+2 * ms, +2 * ms], [-3 * ms, -2 * ms], 'k-', lw=2)
    plt.plot([-2 * ms, -2 * ms], [+2 * ms, +3 * ms], 'k-', lw=2)
    plt.plot([+2 * ms, +2 * ms], [+2 * ms, +3 * ms], 'k-', lw=2)
    plt.plot([-2 * ms, +2 * ms], [-3 * ms, -3 * ms], 'k-', lw=2)
    plt.plot([-2 * ms, +2 * ms], [+3 * ms, +3 * ms], 'k-', lw=2)
    plt.plot([-3 * ms, -2 * ms], [+2 * ms, +2 * ms], 'k-', lw=2)
    plt.plot([-3 * ms, -2 * ms], [-2 * ms, -2 * ms], 'k-', lw=2)
    plt.plot([+2 * ms, +3 * ms], [+2 * ms, +2 * ms], 'k-', lw=2)
    plt.plot([+2 * ms, +3 * ms], [-2 * ms, -2 * ms], 'k-', lw=2)

def DrawCorrection(fig, data, drawbox=True, drawcamoutline=False, drawcampixels=True):

    df = pd.read_csv('full_camera_mapping.cfg', sep='\t')
    cam_x = -df['xpix']  # For lab need to rotate by 180
    cam_y = -df['ypix']  # For lab need to rotate by 180
    row = df['row']
    col = df['col']
    nrows = row.max() + 1
    ncols = col.max() + 1

    image = np.ma.zeros((nrows, ncols))
    image[row, col] = data
    image[0:8, 40:48] = np.ma.masked
    image[0:8, 0:8] = np.ma.masked
    image[40:48, 0:8] = np.ma.masked
    image[40:48, 40:48] = np.ma.masked

    ax = fig.add_subplot(111)

    plt.imshow(image, origin='lower',extent=(np.min(cam_x), np.max(cam_x), np.min(cam_y), np.max(cam_y)),
               cmap='winter', interpolation='none')
    plt.xlabel("Horizontal Distance @Camera (m)")
    plt.ylabel("Vertical Distance @Camera (m)")
    plt.colorbar(label="Correction Factor")

    xminorLocator = AutoMinorLocator()
    ax.xaxis.set_minor_locator(xminorLocator)
    yminorLocator = AutoMinorLocator()
    ax.yaxis.set_minor_locator(yminorLocator)
    plt.tick_params(which='both', width=1)
    plt.tick_params(which='major', length=7)
    plt.tick_params(which='minor', length=4)
    plt.axhline(y=0.0, ls='--', color='black', lw='0.5')
    plt.axvline(x=0.0, ls='--', color='black', lw='0.5')

    if drawbox: DrawBox()
    if drawcamoutline: DrawCameraOutline()
    if drawcampixels: DrawPixels(cam_x, cam_y)

    plt.text(cam_x[0], cam_y[0], "0", horizontalalignment='center')


def main():
    parser = argparse.ArgumentParser(description='Draw results of a laser scan')
    parser.add_argument('-f', '--fname', type=str, help='Correction filename', default="total_correction.txt")
    parser.add_argument('-t', '--type', type=int, help='0-Camera, 1-Laser, 2-Total, -1-all (default)', default=-1)

    args = parser.parse_args()

    cfile = args.fname

    type = args.type
    if type>2:
        print("Invalid type")
        exit()

    pix, flat, laser, total = LoadCorrection(cfile)
    cor = [flat, laser, total]
    cor_title = ["Camera Focal Plane Correction", "Laser Beam Uniformity Correction", "Total Correction"]

    if type>=0:
        fig = plt.figure(1)
        plt.title(cor_title[type])
        DrawCorrection(fig, cor[type], drawbox=True, drawcamoutline=False, drawcampixels=True)

    else:
        for i, c in enumerate(cor):
            fig = plt.figure(i+1)
            plt.title(cor_title[i])
            DrawCorrection(fig, cor[i], drawbox=True, drawcamoutline=True, drawcampixels=False)

    plt.show()




if __name__ == "__main__":
    main()

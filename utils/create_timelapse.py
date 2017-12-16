# -*- coding: utf-8 -*-
import os
import sys
import glob
import time
import itertools
import subprocess
import shutil
import numpy as np
import multiprocessing as mp
import matplotlib.pyplot as plt
from scipy.misc import toimage
import datetime
from sftp import create_sftp_client
counter = 0

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = u'█'):
    """
    Call in a loop to create terminal progress bar
    Parameters
    ----------
    iteration: int 
        current iteration
    total: int
        total iterations
    prefix: str
        prefix string
    suffix: str
        suffix string
    decimals: int
        positive number of decimals in percent complete
    length: int
        character length of bar
    fill: str
        bar fill character
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total: 
        print()

def convert_to_png(f, rot, outpath):
    """
    Parameters
    ----------
    files: list
        list of files to conver to png
    rot: int
        rotate the image counter clock-wise
    outpath: str
        path where to write output files to
    """
    try:
        global counter
        counter += 1
        img = np.fromfile(f, np.uint8).reshape(3840, 5120)
        grn = img[::2, 1::2]
        red = img[::2, ::2]
        blu = img[1::2, 1::2]
        im  = toimage(np.rot90(np.dstack((red, grn, blu)), rot))
        immtime = str(os.path.getmtime(f))
        cam_type = os.path.basename(f).split('_')[1]
        im.save(os.path.join(outpath, cam_type+"-"+immtime+str(".png")))
    except Exception as ex:
        print("Exception in convert_to_png: "+str(ex))

def _topng(params):
    return convert_to_png(*params)

def _create_timelapse(cam_name, pngdir, out_dir):
    """
    Function to create a timelapse for all the 
    png files
    Parameters
    ----------
    cam_name: str
        this is the unique name by which ffmpeg
        will search the directory for files
    pngdir: str
        path where the png files are saved
    out_dir: str
        path where to store the output
    Return
    ------
    The output by the name `cam_name.mp4` will be
    created inside `out_dir`
    """
    # ffmpeg -r 24 -f image2 -s 500x500 -pix_fmt gray \
    # -pattern_type glob -i '2017-07-19png/*d6*.png' -vcodec libx264 -crf 25 d6.mp4
    subprocess.call(["ffmpeg -hide_banner -loglevel panic"
                     + " -r 24"
                     + " -f image2"
                     + " -s 500x500"
                     + " -pix_fmt gray"
                     + " -pattern_type glob"
                     + " -i '{indir}/{cam}-*.png'".format(indir=pngdir, cam=cam_name)
                     + " -vcodec libx264"
                     + " -crf 25"
                     + " {outfile}.mp4".format(outfile=os.path.join(out_dir, 
                                                                    cam_name))
                     + " -y"], 
                    shell=True)

if __name__ == "__main__":
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)
    print("[Starting]: ", today)
    basepath= os.getenv("audubon_datamart")
    remote_tl_dir = os.getenv("dashsense_tl_dir")
    tl_outdir = basepath
    inpath  = os.path.join(basepath, 
                           "{}-{:02d}-{:02d}_night".format(yesterday.year,
                                                           yesterday.month,
                                                           yesterday.day)) 
    pngdir  = os.path.join(basepath, 
                           "{}-{:02d}-{:02d}_png".format(yesterday.year,
                                                         yesterday.month,
                                                         yesterday.day))
    if not os.path.exists(pngdir):
        os.mkdir(pngdir)
    # Get all the files
    d6_path = os.path.join(inpath, "*d6_")
    d9_path = os.path.join(inpath, "*d9_")
    print("Scanning all the D6 files ... ")
    d6_files  = sorted(glob.glob(d6_path+"*.raw"), key=os.path.getmtime)
    print("Scanning all the D9 files ... ")
    d9_files  = sorted(glob.glob(d9_path+"*.raw"), key=os.path.getmtime)
    len_d6 = len(d6_files)
    len_d9 = len(d9_files)
    # Go ballistic with the processor
    p = mp.Pool(60)
    for i, _ in enumerate(p.imap_unordered(_topng, zip(iter(d6_files), itertools.repeat(3), itertools.repeat(pngdir)))):
        printProgressBar(i, len_d6, prefix='D6 Progress:', suffix='Complete', length=50)
    print()
    print()
    for j, _ in enumerate(p.imap_unordered(_topng, zip(iter(d9_files), itertools.repeat(1), itertools.repeat(pngdir)))):
        printProgressBar(j, len_d9, prefix='D9 Progress:', suffix='Complete', length=50)
    print()
    print()
    print("Creating Timelapse ... ")
    print(pngdir)
    _create_timelapse(cam_name="d6", pngdir=pngdir, out_dir=tl_outdir)
    _create_timelapse(cam_name="d9", pngdir=pngdir, out_dir=tl_outdir)
    host = "dashsense.cusp.nyu.edu"
    port = 22
    username = "mohitsharma44"
    password = os.getenv("dashsense_pass")
    keyfilepath = None
    sftpclient = create_sftp_client(host, port, username, password, keyfilepath, 'DSA')
    for _file in glob.glob(os.path.join(tl_outdir, "*.mp4")):
        print("SFTPing: "+str(_file))
        sftpclient.put(_file, os.path.join(remote_tl_dir, os.path.basename(_file)))
    sftpclient.close()
    # (Force-)Cleanup the pngdir
    shutil.rmtree(pngdir, ignore_errors=True)
    print("[Finished]: ",datetime.datetime.now())
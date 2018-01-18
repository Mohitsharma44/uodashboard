# -*- coding: utf-8 -*-
##
##
## Check the code first! It maybe deleting the RAW files as well!!!!
##
##
import os
import re
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
        rgb = np.dstack((red, grn, blu))
        # gain
        rgb = (rgb * 5.0).clip(0, 255).astype(np.uint8)
        im  = toimage(np.rot90(rgb, rot))
        immtime = str(os.path.getmtime(f))
        cam_type = os.path.basename(f).split('_')[1]
        #im.save(os.path.join(outpath, cam_type+"-"+immtime+str(".png")))
        im.save(os.path.join(outpath, cam_type+"-"+f.split("_")[-1][:-4]+str(".png")))
    except Exception as ex:
        print("Exception in convert_to_png: "+str(ex))

def _topng(params):
    return convert_to_png(*params)

def _convert_mp4_webm(fname):
    """
    Helper function to call ffmpeg for
    converting mp4 file to webm format
    """
    subprocess.call(["ffmpeg -hide_banner -loglevel panic"
                     + " -i {fname}".format(fname=fname)
                     + " -c:v libvpx-vp9"
                     + " -crf 30"
                     + " -b:v 0"
                     + " {outfile}".format(outfile=os.path.join(out_dir,
                                                               fname[:-3]+"webm"))
                     + " -y"],
                    shell=True)

def create_timelapse(params):
    return _create_timelapse(*params)

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
    outfile = "{}.mp4".format(os.path.join(out_dir, cam_name))
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
                     + " {outfile}".format(outfile=outfile)
                     + " -y"],
                    shell=True)
    _convert_mp4_webm(outfile)

def natural_sort(l): 
    convert = lambda text: int(text) if text.isdigit() else text.lower() 
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(l, key = alphanum_key)
    
if __name__ == "__main__":
    cam_names = ["d6", "d9"]
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=12)
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
    #d6_files  = sorted(glob.glob(d6_path+"*.raw"), key=os.path.getctime)
    d6_files  = natural_sort(glob.glob(d6_path+"*.raw"))
    print("Scanning all the D9 files ... ")
    #d9_files  = sorted(glob.glob(d9_path+"*.raw"), key=os.path.getctime)
    d9_files  = natural_sort(glob.glob(d9_path+"*.raw"))
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
    for k, _ in enumerate(p.map(_create_timelapse, zip(cam_name=iter(cam_names), pngdir=itertools.repeat(pngdir), outdir=itertools.repeat(outdir)))):
        printProgressBar(k, len(cam_names), prefix='Timelapse Progress', suffix='Complete', length=50)
    print()
    print()
    #d6mp4 = _create_timelapse(cam_name="d6", pngdir=pngdir, out_dir=tl_outdir)
    #d9mp4 = _create_timelapse(cam_name="d9", pngdir=pngdir, out_dir=tl_outdir)
    #d6webm = _convert_mp4_webm(fname=d6mp4)
    #d9webm = _convert_mp4_webm(fname=d9mp4)
    """
    host = "dashsense.cusp.nyu.edu"
    port = 22
    username = "mohitsharma44"
    password = os.getenv("dashsense_pass")
    keyfilepath = None
    sftpclient = create_sftp_client(host, port, username, password, keyfilepath, 'DSA')
    ftypes = ["*.mp4", "*.webm"]
    for ftype in ftypes:
        for _file in glob.glob(os.path.join(tl_outdir, ftype)):
            print("SFTPing: "+str(_file))
            sftpclient.put(_file, os.path.join(remote_tl_dir, os.path.basename(_file)))
    sftpclient.close()
    """
    # (Force-)Cleanup the pngdir
    shutil.rmtree(pngdir, ignore_errors=True)
    ##
    ##
    ## -- Deleting RAW files as well!!
    ##
    ##
    # For test cleaning rawdir
    shutil.rmtree(inpath, ignore_errors=True)
    print("[Finished]: ",datetime.datetime.now())

"""
Module to Upload file to the server
"""

import pycurl
import os
import time
import asyncore
import pyinotify
import numpy as np
from io import BytesIO
from scipy.misc import toimage, imresize
from collections import deque
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from watchdog.events import PatternMatchingEventHandler

MONITOR_DIR = "/projects/projects/project-audubon_uo/datamarts/audubon_imgs_live"
wm = pyinotify.WatchManager()
mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_MOVED_TO # watched events

# Rotation mapping for Audubon Cameras
rotation_mapping = {
    "d6": 3,
    "d9": 1,
}

def uploadFile(filename, cam_name):
    """
    Upload file to `URL`
    Parameters
    ----------
    filename: str
        filename (with path) to be uploaded
    cam_name: str
        name of the camera to send in HTTPHeader

    Returns
    -------
    response: BytesIO
        response returned by the server.
    """
    URL = "128.122.72.52:8888/upload"
    curl = pycurl.Curl()
    response = BytesIO()

    curl.setopt(curl.POST, 1)
    curl.setopt(curl.URL, URL)
    curl.setopt(curl.HTTPHEADER, ['cam_name: ' + cam_name])
    curl.setopt(curl.HTTPPOST, [('file1',
                                 (curl.FORM_FILE,
                                  os.path.abspath(filename))
                                 )])
    curl.setopt(curl.WRITEFUNCTION, response.write)
    print("Uploading file " + str(filename))
    curl.perform()
    curl.close()
    if response.getvalue() == b"OK":
        print("Successfully Uploaded")
    else:
        print("Cannot Upload: " + str(response.getvalue()))
    os.remove(os.path.abspath(filename))
    return response

def _read_raw(fname, width, height, binfac=1):
    """
    Function to read a binary raw image
    Parameters
    ----------
    fname: str
        absolute file path to read the image from
    width: int
    height: int
    binfac: int
        If the returned array should be binned
    Returns
    -------
    np.ndarray:
        2D numpy array
    """
    if os.path.getsize(fname) == width*height:
        # Return binned image by bin factor
        return np.fromfile(fname, np.uint8).reshape(height, width)[::binfac, ::binfac]
    else:
        print("ERROR: File is not in binary format or the size is not correct")
        return None

def topng(fname=None, rot=1, height=3840, width=5120, outpath=None):
    """
    Convert image to png format
    Parameters
    ----------
    fname: str
        absolute path to read the image file
    rot: int
        if the image is rotated, image will be rotated by rot x 90deg
    height: int
    width: int
    outpath: str
        *only* directory to output the png file to
    """
    imgarr = _read_raw(fname, width, height, binfac=1)
    if imgarr is not None:
        img = np.rot90(imgarr, rot)
        resized_img = imresize(img, 60)
        im  = toimage(resized_img)
        outfile = os.path.join(outpath,
                               os.path.basename(fname)[:-3]+str("png"))
        im.save(outfile)
        return outfile

class EventHandler(pyinotify.ProcessEvent):
    def process_IN_MOVED_TO(self, event):
        if event.pathname.endswith(".raw"):
            try:
                filename = event.pathname
                rot = rotation_mapping[os.path.basename(filename).split('_')[1]]
                outfile = topng(fname=filename, rot=rot, outpath='./')
                if outfile:
                    cam_name = os.path.basename(outfile).split('_')[1]
                    uploadFile(outfile, cam_name)
            except Exception as ex:
                print("ERROR: "+str(ex))


if __name__ == "__main__":
    notifier = pyinotify.AsyncNotifier(wm, EventHandler())
    wdd = wm.add_watch(MONITOR_DIR, mask, rec=True)
    print("Monitoring: ", MONITOR_DIR)
    asyncore.loop()

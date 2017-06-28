"""
Module to Upload file to the server
"""

import pycurl
import os
import time
import numpy as np
from io import BytesIO
from scipy.misc import toimage
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

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
    URL = "localhost:8888/upload"
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
    return response

def _read_raw(fname, width, height):
    """
    Function to read a binary raw image
    Parameters
    ----------
    fname: str
        absolute file path to read the image from
    Returns
    -------
    np.ndarray:
        2D numpy array
    """
    if os.path.getsize(fname) == width*height:
        return np.fromfile(fname, np.uint8).reshape(height, width)
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
    imgarr = _read_raw(fname, width, height)
    if imgarr:
        img = np.rot90(imgarr, rot)
        im  = toimage(img)
        outfile = os.path.join(outpath,
                               os.path.basename(fname)[:-3]+str("png"))
        im.save(outfile)
        return outfile

class FsHandler(FileSystemEventHandler):
    """
    Class to handle events when a new file is created
    """
    def on_created(self, event):
        if event.is_directory:
            pass
        else:
            print(event.src_path)
            fname = event.src_path
            if fname.endswith("raw"):
                outfile = topng(event.src_path)
                ## Pulling cam name from filename. Make sure format
                ## is consistent througout
                if outfile:
                    cam_name = os.path.basename(outfile).split('_')[1]
                    uploadFile(outfile, cam_name)


class MonitorDir():
    """
    Function to monitor a directory for new files
    Parameters
    ----------
    path: str
        path to monitor
    """
    def __init__(self, path):
        self.path = path
        self.fs_observer = Observer()

    def run(self):
        self.fs_event_handler = FsHandler()
        self.fs_observer.schedule(self.fs_event_handler,
                                  self.path,
                                  recursive=False)
        self.fs_observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nWARNING: Stop Monitoring")
            self.fs_observer.stop()
        self.fs_observer.join()

if __name__ == "__main__":
    path_to_monitor = os.path.abspath("./")
    print("Monitoring: ", path_to_monitor)
    monit = MonitorDir(path_to_monitor)
    monit.run()

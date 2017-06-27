"""
Module to Upload file to the server
"""

import pycurl
import os
from io import BytesIO

def uploadFile(filename):
    """
    Upload file to `URL`
    Parameters
    ----------
    filename: str
        filename (with path) to be uploaded

    Returns
    -------
    response: BytesIO
        response returned by the server.
    """
    URL = "localhost:8888/upload"
    ID = "5 MTC"
    curl = pycurl.Curl()
    response = BytesIO()

    curl.setopt(curl.POST, 1)
    curl.setopt(curl.URL, URL)
    curl.setopt(curl.HTTPHEADER, ['id: ' + ID])
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

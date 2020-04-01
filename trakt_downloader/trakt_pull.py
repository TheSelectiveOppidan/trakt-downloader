#!/usr/bin/env python

from trakt_downloader import TraktPuller
import os

def go():
    TraktPuller.start(str(os.getcwd()))
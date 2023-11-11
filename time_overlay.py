import cv2, time, os, sys, subprocess, shlex, re
import datetime as dt
import pytz
import csv
import os

class TimeOverlay:

    def __init__(self):
        self.in_path = None
        self.out_path = None
        self.in_filename = None
        self.out_filename = None

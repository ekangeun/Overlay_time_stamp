import cv2, time, os, sys, subprocess, shlex, re
import datetime as dt
import pytz
import csv
import os


class VideoResizer:

    def __init__(self):
        pass

    def get_resizing_resolution(self, video_width, video_height, new_resol):
        if video_width < video_height:
            regular_video_width = new_resol[1]
        else:
            regular_video_width = new_resol[0]
        regular_video_height = regular_video_width / video_width * video_height
        return [regular_video_width, regular_video_height]

    def resize_video(self, input_file_name, output_file_name, resol):
        print('Resize video ...')
        command = ['ffmpeg', '-i', input_file_name, "-vf", "scale=" + str(resol[0]) + ':' + str(resol[1]),
                   output_file_name]
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        print(out)
        if err:
            print("========= error ========")
            print(err)
import cv2, time, os, sys, subprocess, shlex, re
import datetime as dt
import pytz
import csv
import os

from audio_handle import AudioHandler
from date_time_handle import DateTimeHandler
from meta_handle import MetaDataHandler
from overlayer import TimeOverlay
from video_resize import VideoResizer


class VideoProcessor:

    def __init__(self, in_path, out_path, filename, crop):
        self.regular_video_height = None
        self.regular_video_width = None
        self.font_scale = None
        self.box_length = None
        self.box_width = None
        self.basey = None
        self.basex = None
        self.initial_time = None
        self.cv_out_video = None
        self.time_str = None
        self.total_frames = None
        self.crop_video_size = None
        self.video_size = None
        self.height = None
        self.width = None
        self.fps = None
        self.cv_in_video = None
        self.crop_video = crop
        if in_path[-1] != '/':
            in_path = in_path + '/'
        if out_path[-1] != '/':
            out_path = out_path + '/'
        self.in_path = in_path
        self.out_path = out_path
        self.in_video_filename = filename + '.mp4'
        self.resize_video_filename = filename + '_resized.mp4'
        self.out_video_filename = filename + '.mp4'
        self.telemetry_filename = filename + '_Hero7 Black-GPS5.csv'
        self.audio_filename = filename + '.wav'
        self.video_with_time_filename = filename + '_with_time.mp4'
        self.telemetry_data = []
        self.telemetry_okay = False

        self.cv_in_video = cv2.VideoCapture(self.in_path + self.in_video_filename)
        self.org_width = self.cv_in_video.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.org_height = self.cv_in_video.get(cv2.CAP_PROP_FRAME_HEIGHT)

        if self.is_regular_size():
            self.video_org_size_filename = filename + '.mp4'
        else:
            self.video_org_size_filename = filename + 'org.mp4'

    def is_regular_size(self):
        return (self.org_width == 1280) or (self.org_height == 720)

    def set_env(self):

        # if not self.crop_video:
        #     self.cv_in_video = cv2.VideoCapture(self.out_path + self.resize_video_filename)
        # else:
        self.cv_in_video = cv2.VideoCapture(self.in_path + self.in_video_filename)

        self.fps = self.cv_in_video.get(cv2.CAP_PROP_FPS)
        self.width = self.cv_in_video.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.cv_in_video.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.video_size = (int(self.width), int(self.height))
        if self.crop_video:
            self.crop_video_size = \
                int(self.width * 3 / 4) - int(self.width / 4), (int(self.height * 3 / 4) - int(self.height / 4))
        else:
            self.crop_video_size = self.video_size

        self.total_frames = self.cv_in_video.get(cv2.CAP_PROP_FRAME_COUNT)
        codec = cv2.VideoWriter_fourcc(*'DIVX')
        if self.crop_video:
            self.cv_out_video = cv2.VideoWriter(self.out_path + self.video_with_time_filename,
                                                codec, self.fps, self.crop_video_size, 1)
        else:
            self.cv_out_video = cv2.VideoWriter(self.out_path + self.video_with_time_filename,
                                                codec, self.fps, self.video_size, 1)
        self.time_str = '2022-03-04 12:29:02'
        self.initial_time = dt.datetime.strptime(self.time_str, "%Y-%m-%d %H:%M:%S")
        if self.video_size[0] > self.video_size[1]:
            x_width = self.video_size[0]
            y_width = self.video_size[1]
            x_width2 = self.crop_video_size[0]
            y_width2 = self.crop_video_size[1]
        else:
            x_width = self.video_size[1]
            y_width = self.video_size[0]
            x_width2 = self.crop_video_size[1]
            y_width2 = self.crop_video_size[0]

        if self.crop_video:
            self.basex = int(x_width / 4)
            self.basey = int(y_width / 4)
            self.box_width = int(x_width2 * 0.4)
            self.box_length = int(y_width2 * 0.07)
            self.font_scale = max(int(x_width2 / 1386), 1)
        else:
            self.basex = int(x_width * 0)
            self.basey = int(y_width * 0)
            self.box_width = int(x_width * 0.3)
            self.box_length = int(y_width * 0.05)
            self.font_scale = max(int(x_width / 1386), 1)



    def do_overlay(self):

        if not self.crop_video:
            print("Resize video to regular resolution for processing.")
            video_in = cv2.VideoCapture(self.in_path + self.in_video_filename)
            video_height = video_in.get(cv2.CAP_PROP_FRAME_HEIGHT)
            video_width = video_in.get(cv2.CAP_PROP_FRAME_WIDTH)
            video_resizer = VideoResizer()
            [self.regular_video_width, self.regular_video_height] = video_resizer.get_resizing_resolution(video_width,
                                                                                                 video_height,
                                                                                                 [1920, 1080])
            # self.resize_video(self.in_path + self.in_video_filename,
            #                   self.out_path + self.resize_video_filename,
            #                   [self.regular_video_width, self.regular_video_height])

        self.set_env()

        dat_time = DateTimeHandler(self.in_path, self.in_video_filename)
        time_overlay = TimeOverlay(self.cv_in_video, self.cv_out_video, dat_time.get_time_information(),
                                   self.crop_video)
        time_overlay.do_overlay()

        audio_handler = AudioHandler(self.out_path)
        audio_handler.extract_audio(self.in_path + self.in_video_filename)
        audio_handler.audio_insert(self.out_path + self.video_with_time_filename,
                                   self.out_path + self.video_org_size_filename,)

        if self.crop_video:
            video_resizer = VideoResizer()
            video_resizer.resize_video(self.out_path + self.video_org_size_filename,
                              self.out_path + self.out_video_filename,
                              video_resizer.get_resizing_resolution(int(self.width / 4), int(self.height / 4), [1920, 1080]))
            if os.path.exists(self.out_path + self.video_org_size_filename):
                os.remove(self.out_path + self.video_org_size_filename)
        else:
            if not self.is_regular_size():
                video_resizer = VideoResizer()
                video_resizer.resize_video(self.out_path + self.video_org_size_filename,
                                  self.out_path + self.out_video_filename,
                                  video_resizer.get_resizing_resolution(self.regular_video_width, self.regular_video_height,
                                                               [1280, 720]))

                if os.path.exists(self.out_path + self.video_org_size_filename):
                    os.remove(self.out_path + self.video_org_size_filename)

        meta_handler = MetaDataHandler(self.out_path, self.video_org_size_filename, dat_time.get_file_created_time())
        meta_handler.set_time_info()
        meta_handler.remove_backup_file()

        if os.path.exists(self.out_path + self.resize_video_filename):
            os.remove(self.out_path + self.resize_video_filename)

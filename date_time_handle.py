import cv2, time, os, sys, subprocess, shlex, re
import datetime as dt
import pytz


class DateTimeHandler:

    def __init__(self, in_path, in_video_filename):
        self.file_name = in_path + in_video_filename

        command_line = ['ffprobe', '-show_format', '-pretty', '-loglevel', 'quiet', self.file_name]
        p = subprocess.Popen(command_line, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.stdout_data, stderr_data = p.communicate()
        print("==========output==========")
        print(self.stdout_data)
        print(stderr_data)


    def get_file_created_time(self):
        return str(self.stdout_data.splitlines()[14][18:37])[2:-1]

    def get_time_information(self):
        time_info = str(self.stdout_data.splitlines()[14][18:37])
        time_info_str = time_info[2:-1]
        time_zone_info = time_info[13:15]

        if int(time_zone_info) > 10:
            initial_time = dt.datetime.strptime(time_info_str, "%Y-%m-%d %H:%M:%S")
        else:
            local_tz = pytz.timezone("Asia/Seoul")
            initial_time = dt.datetime.strptime(time_info_str, "%Y-%m-%d %H:%M:%S")\
                .replace(tzinfo=pytz.utc).astimezone(local_tz)

        return initial_time

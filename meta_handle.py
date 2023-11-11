import subprocess
import os


class MetaDataHandler:

    def __init__(self, out_path, out_video_filename, time_str):
        self.file_name = out_path + out_video_filename
        self.time_str = time_str

    def remove_backup_file(self):
        if os.path.exists(self.file_name + '_original'):
            os.remove(self.file_name + '_original')

    def set_time_info(self):
        command = ['exiftool', self.file_name,
                   '-FileModifyDate=' + self.time_str,
                   '-FileCreateDate=' + self.time_str,
                   '-CreateDate=' + self.time_str,
                   '-api', 'QuickTimeUTC'
                   ]
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        print("==========output==========")
        print(out)
        if err:
            print("========= error ========")
            print(err)

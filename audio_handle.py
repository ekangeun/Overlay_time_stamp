import subprocess
import os


class AudioHandler:

    def __init__(self, out_path):
        self.out_path = out_path
        self.audio_filename = 'tmp_audio.wav'

    def extract_audio(self, input_file_name):
        print('Extract audio ...')
        if os.path.exists(self.out_path + self.audio_filename):
            os.remove(self.out_path + self.audio_filename)
        command = ['ffmpeg', '-i', input_file_name,
                   '-f', 'wav', '-sb', '192000', '-vn', self.out_path + self.audio_filename]
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        print(stdout)
        if stderr:
            print("========= error ========")
            print(stderr)

    def audio_insert(self, video_input_file_name, video_output_file_name):
        print('\nInsert audio ...')
        if os.path.exists(video_output_file_name):
            os.remove(video_output_file_name)
        command = ['ffmpeg', '-i', video_input_file_name,
                   '-i', self.out_path + self.audio_filename,
                   "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-shortest",
                   video_output_file_name]
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        print(out)
        if err:
            print("========= error ========")
            print(err)

        if os.path.exists(self.out_path + self.audio_filename):
            os.remove(self.out_path + self.audio_filename)
        if os.path.exists(video_input_file_name):
            os.remove(video_input_file_name)

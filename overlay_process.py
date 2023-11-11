import cv2
import time
import sys
import video_timestamp
import picture_timestamp
import datetime as dt
import pandas as pd

gd = { '0' : [37.209513, 127.047074], \
       'sinchang2' : [37.209513, 127.047074],\
                   'anhwajung' : [37.210158, 127.048344],\
                   'hanmaeumcho_4' : [37.208314, 127.052571],\
'hanmaeumcho_3' : [37.208089, 127.055208],\
                   'soopsockcho' : [37.206592, 127.059927],\
                   'hanmaeumpraza' : [37.214546, 127.044956],\
                   'chamkinder' : [37.206956, 127.041831],\
                   'goobongwoonam' : [37.207439, 127.042840],\
                   'byungjumdoseoguan' : [37.212872, 127.046265],\
                   'greenpark' : [37.211611, 127.043772],\
                   'gongyoungparkinglot' : [37.213076, 127.039791]
                   }

# 정든마을신창비바페밀리리2차 앞 교차로[37.209513, 127.047074]
# 안화중학교사거리 [37.210158, 127.048344]
# 한마음초교사거리 [37.208314, 127.052571]
# 숲속초교사거리 [37.206592, 127.059927]
# 한마음프라자사거리 [37.214546, 127.044956]

input_table = pd.read_csv('input.csv', dtype=str)

picture_name_list = [x for x in list(input_table['pic_name']) if str(x) != 'nan']
video_file_name_list = [x for x in list(input_table['video_name']) if str(x) != 'nan']
gps_info_list = [gd[s] for s in list(input_table['gps'])]
time_offset_list = [x for x in list(input_table['time_offset']) if str(x) != 'nan']
crop_on = [x for x in list(input_table['crop']) if str(x) != 'nan']

# picture_name_list = ['8975']
# video_file_name_list = ['8975']
# gps_info_list = [gd['hanmaeumcho_3']]

in_path = 'video_input'
in_path_picture = 'picture_input'
out_path = 'output'

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")


for i_pic, picture_filename in enumerate(picture_name_list):
    try:
        if picture_filename != str(0):
            gps_info = gps_info_list[i_pic]
            time_offset_sec = int(time_offset_list[i_pic])
            video_overlay = picture_timestamp.PictureProcessor(in_path_picture, out_path, picture_filename, time_offset_sec, gps_info)
            video_overlay.do_overlay()
    except:
        print('Warnning: picture processing error')


for i_vid, video_filename in enumerate(video_file_name_list):
    try:
        if video_filename != str(0):
            video_overlay = video_timestamp.VideoProcessor(in_path, out_path, video_filename, str2bool(crop_on[i_vid]))
            video_overlay.do_overlay()
    except:
        print('Warnning: video processing error')

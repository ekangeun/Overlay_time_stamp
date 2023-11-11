import exifread
from exif import Image
import os
import os.path
from os import path

import piexif
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from fractions import Fraction
import datetime as dt
from datetime import datetime
from PIL import ExifTags
import cv2

import pywintypes, win32file, win32con
import dateutil.parser


def dms2dd(tup1):
    dd = float(tup1[0][0])/float(tup1[0][1]) + float(tup1[1][0])/float(tup1[1][1])/60 + float(tup1[2][0])/float(tup1[2][1])/(60*60)
    return dd


def to_deg(value, loc):
    """convert decimal coordinates into degrees, munutes and seconds tuple
    Keyword arguments: value is float gps-value, loc is direction list ["S", "N"] or ["W", "E"]
    return: tuple like (25, 13, 48.343 ,'N')
    """
    if value < 0:
        loc_value = loc[0]
    elif value > 0:
        loc_value = loc[1]
    else:
        loc_value = ""
    abs_value = abs(value)
    deg =  int(abs_value)
    t1 = (abs_value-deg)*60
    min = int(t1)
    sec = round((t1 - min)* 60, 5)
    return (deg, min, sec, loc_value)


class PictureProcessor:

    def __init__(self, in_path, out_path, filename, time_offset_sec, gps_info):
        if in_path[-1] != '/':
            in_path = in_path + '/'
        if out_path[-1] != '/':
            out_path = out_path + '/'
        self.in_path = in_path
        self.out_path = out_path
        self.in_picture_filename = filename + '.jpg'
        self.out_picture_filename = filename + '.jpg'
        self.temp_picture_filename = filename + '_temp.jpg'
        self.width = None
        self.height = None
        try:
            self.meta_data = piexif.load(Image.open(self.in_path + self.in_picture_filename).info['exif'])
        except:
            print('Error: can\'t open file: {0}'.format(self.in_path + self.in_picture_filename))
        date_info_tmp = self.meta_data['Exif'][piexif.ExifIFD.DateTimeOriginal]
        d = datetime.strptime(date_info_tmp.decode('utf-8'), '%Y:%m:%d %H:%M:%S') + dt.timedelta(
            seconds=time_offset_sec)
        self.date_info = d.strftime('%Y-%m-%d %H:%M:%S')  # convert string
        if piexif.GPSIFD.GPSLatitude in self.meta_data['GPS'] and piexif.GPSIFD.GPSLongitude in self.meta_data['GPS']:
            self.gps_info = [dms2dd(self.meta_data['GPS'][piexif.GPSIFD.GPSLatitude]),
                             dms2dd(self.meta_data['GPS'][piexif.GPSIFD.GPSLongitude])]
        else:
            self.gps_info = gps_info
        self.image = cv2.imread(self.in_path + self.in_picture_filename)
        # except:
        #     print('Cannot find {0}.'.format(self.in_path + self.in_picture_filename))

    def insert_date(self):
        info = self.meta_data['0th']
        exif = self.meta_data['Exif']

        # Rotate image
        # if info[piexif.ImageIFD.Orientation] == 3:
        #     image = cv2.rotate(image, cv2.ROTATE_180)
        # elif info[piexif.ImageIFD.Orientation] == 6:
        #     image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        # elif info[piexif.ImageIFD.Orientation] == 8:
        #     image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

        orientation = info[piexif.ImageIFD.Orientation]
        if orientation == 6 | orientation == 8:
            xwidth = self.meta_data['Exif'][40963]
            ywidth = self.meta_data['Exif'][40962]
        else:
            xwidth = self.meta_data['Exif'][40962]
            ywidth = self.meta_data['Exif'][40963]

        if (xwidth == 4000):
            basex = int(xwidth * 0.005)
            box_width = int(xwidth * 0.26)
        else:
            basex = int(xwidth * 0.005)
            box_width = int(xwidth * 0.27)

        if (ywidth == 3000):
            basey = int(ywidth * 0.005)
            box_length = int(ywidth * 0.0418)
        else:
            basey = int(ywidth * 0.005)
            box_length = int(ywidth * 0.0418)

        # Add transparent box
        overlay = self.image.copy()
        alpha = 0.6  # Transparency factor.

        cv2.rectangle(overlay, (basex, basey),
                      (basex + box_width, basey + box_length), (0, 0, 0), -1)

        # cv2.rectangle(overlay, (basex, basey + box_length + 1),
        #               (basex + box_width, int(basey + box_length + box_length)), (0, 0, 0), -1)

        # Following line overlays transparent rectangle over the image
        self.image = cv2.addWeighted(overlay, alpha, self.image, 1 - alpha, 0)

        cv2.putText(self.image, self.date_info, (int(basex + box_width * 0.01),
                                                 int(basey + box_length * 0.7)),
                    cv2.FONT_HERSHEY_DUPLEX, int(xwidth/1386),
                    (255, 255, 255), thickness=5, lineType=cv2.LINE_AA)

        lat = float(self.gps_info[0])
        lat = "{:.6f}".format(lat)
        lon = float(self.gps_info[1])
        lon = "{:.6f}".format(lon)

        txt = 'Latitude: ' + str(lat)
        # cv2.putText(self.image, txt, (int(basex + box_width * 0.01),
        #                               int(basey + box_length + box_length * 0.3 * 0.9)),
        #             cv2.FONT_HERSHEY_DUPLEX, int(xwidth/1546),
        #             (255, 255, 255), thickness=2, lineType=cv2.LINE_AA)
        # txt = 'Longitude: ' + str(lon)
        # cv2.putText(self.image, txt, (int(basex + box_width * 0.01), int(basey + box_length + box_length * 0.9 * 0.9)),
        #             cv2.FONT_HERSHEY_DUPLEX, int(xwidth / 1546),
        #             (255, 255, 255), thickness=2, lineType=cv2.LINE_AA)

        cv2.imwrite(self.out_path + self.temp_picture_filename, self.image)

    def set_meta_data(self):
        img_with_date_stamp = Image.open(self.out_path + self.temp_picture_filename)
        self.meta_data['0th'][piexif.ImageIFD.DateTime] = self.date_info
        self.meta_data['0th'][piexif.ImageIFD.Orientation] = 1
        self.meta_data['Exif'][piexif.ExifIFD.DateTimeOriginal] = self.date_info
        self.meta_data['Exif'][piexif.ExifIFD.DateTimeDigitized] = self.date_info

        try:
            del self.meta_data['Exif'][piexif.ExifIFD.SceneType]
        except:
            pass

        meta_bytes = piexif.dump(self.meta_data)
        img_with_date_stamp.save(self.out_path + self.out_picture_filename, exif=meta_bytes)
        os.remove(self.out_path + self.temp_picture_filename)

    def changeFileCreationTime(self):
        newtime = dateutil.parser.parse(self.date_info)
        wintime = pywintypes.Time(newtime)
        winfile = win32file.CreateFile(
            self.out_path + self.out_picture_filename, win32con.GENERIC_WRITE,
            win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
            None, win32con.OPEN_EXISTING,
            win32con.FILE_ATTRIBUTE_NORMAL, None)

        win32file.SetFileTime(winfile, wintime, wintime, wintime)

        winfile.close()

    def do_overlay(self):

        self.insert_date()
        self.set_meta_data()
        self.changeFileCreationTime()


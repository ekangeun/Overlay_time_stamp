import cv2, time, os, sys, subprocess, shlex, re
import datetime as dt
import pytz
import csv
import os


class GpsHandler:
    def __init__(self):
        pass

    def get_telemetry_data(self):
        if os.path.isfile(self.in_path + self.telemetry_filename):
            print('Found telemetry data in ' + self.in_path + '.')
            with open(self.in_path + self.telemetry_filename, newline='') as csvfile:
                self.telemetry_okay = True
                reader = csv.reader(csvfile, delimiter=',', quotechar='"')
                for row in reader:
                    self.telemetry_data.append(row)
        else:
            print('No telemetry data in ' + self.in_path + '.')


    def insert_gps_info(self, image, current_frame):
        target_row = 1
        if self.telemetry_okay:
            for i in range(target_row, len(self.telemetry_data)):
                if int(current_frame) <= float(self.telemetry_data[i][0]):
                    target_row = i
                    break

            lat = float(self.telemetry_data[target_row][2])
            lat = "{:.6f}".format(lat)
            lon = float(self.telemetry_data[target_row][3])
            lon = "{:.6f}".format(lon)
            alt = float(self.telemetry_data[target_row][4])
            alt = "{:.1f}".format(alt)
            speed = float(self.telemetry_data[target_row][5])
            speed = "{:.1f}".format(speed)

            overlay = image.copy()
            alpha = 0.6  # Transparency factor.

            cv2.rectangle(overlay, (self.basex, self.basey + self.box_length + 1),
                          (self.basex + self.box_width, int(self.basey + self.box_length + self.box_length)), (0, 0, 0),
                          -1)

            image_with_rectangle = cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)

            txt = 'Lat: ' + str(lat) + ' Lon: ' + str(lon) + ' Alt: ' + str(alt) + '[m]'
            cv2.putText(image_with_rectangle, txt,
                        (int(self.basex + self.box_width * 0.01),
                         int(self.basey + self.box_length + self.box_length * 0.2 * 0.9)),
                        cv2.FONT_HERSHEY_DUPLEX, self.font_scale,
                        (0, 0, 0), thickness=10, lineType=cv2.LINE_AA)
            cv2.putText(image_with_rectangle, txt,
                        (int(self.basex + self.box_width * 0.01),
                         int(self.basey + self.box_length + self.box_length * 0.2 * 0.9)),
                        cv2.FONT_HERSHEY_DUPLEX, self.font_scale,
                        (255, 255, 255), thickness=2, lineType=cv2.LINE_AA)

            txt = 'Speed: ' + str(speed) + '[m/s]'
            cv2.putText(image_with_rectangle, txt,
                        (int(self.basex + self.box_width * 0.01),
                         int(self.basey + self.box_length + self.box_length * 0.8 * 0.9)),
                        cv2.FONT_HERSHEY_DUPLEX, self.font_scale,
                        (0, 0, 0), thickness=10, lineType=cv2.LINE_AA)
            cv2.putText(image_with_rectangle, txt,
                        (int(self.basex + self.box_width * 0.01),
                         int(self.basey + self.box_length + self.box_length * 0.8 * 0.9)),
                        cv2.FONT_HERSHEY_DUPLEX, self.font_scale,
                        (255, 255, 255), thickness=2, lineType=cv2.LINE_AA)

            return image_with_rectangle
        else:
            return image
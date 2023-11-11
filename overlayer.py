import cv2, time, sys
import datetime as dt


class TimeOverlay:
    def __init__(self, cv_in_video, cv_out_video, initial_time, crop_video):
        self.initial_time = initial_time
        self.cv_in_video = cv_in_video
        self.cv_out_video = cv_out_video
        self.total_frames = self.cv_in_video.get(cv2.CAP_PROP_FRAME_COUNT)
        self.width = self.cv_in_video.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.cv_in_video.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.crop_video = crop_video

    def get_time_stamp_box_shape(self):
        x_width, y_width = self.get_image_size((int(self.width), int(self.height)))

        if self.crop_video:
            basex = int(x_width / 4)
            basey = int(y_width / 4)
            box_width = int(x_width * 0.23)
            box_length = int(y_width * 0.05)
        else:
            basex = int(x_width * 0)
            basey = int(y_width * 0)
            box_width = int(x_width * 0.23)
            box_length = int(y_width * 0.05)

        return [basex, basey, box_width, box_length]

    def get_image_size(self, video_size):
        if video_size[0] > video_size[1]:
            x_width = video_size[0]
            y_width = video_size[1]
        else:
            x_width = video_size[1]
            y_width = video_size[0]
        return x_width, y_width

    def get_font_scale(self):
        return max(self.get_image_size((int(self.width), int(self.height)))[0] / 840, 1)

    def get_frame_image(self):
        success, image = self.cv_in_video.read()
        elapsed_time = self.cv_in_video.get(cv2.CAP_PROP_POS_MSEC)
        current_frame = self.cv_in_video.get(cv2.CAP_PROP_POS_FRAMES)

        return image, elapsed_time, current_frame

    def insert_date(self, image, date_info):

        # Add transparent box
        overlay = image.copy()
        alpha = 0.6  # Transparency factor.

        [basex, basey, box_width, box_length] = self.get_time_stamp_box_shape()
        font_scale = self.get_font_scale()

        cv2.rectangle(overlay, (basex, basey), (basex + box_width, basey + box_length), (0, 0, 0), -1)

        # Overlays transparent rectangle over the image
        image_with_rectangle = cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)

        # Add text to image
        cv2.putText(image_with_rectangle, date_info,
                    (int(basex + box_width * 0.01), int(basey + box_length * 0.7)),
                    cv2.FONT_HERSHEY_PLAIN, font_scale,
                    (0, 0, 0), thickness=9, lineType=cv2.LINE_AA)
        cv2.putText(image_with_rectangle, date_info,
                    (int(basex + box_width * 0.01), int(basey + box_length * 0.7)),
                    cv2.FONT_HERSHEY_PLAIN, font_scale,
                    (255, 255, 255), thickness=2, lineType=cv2.LINE_AA)

        return image_with_rectangle

    def set_frame_image(self, image):
        self.cv_out_video.write(image)

    def show_frame_image(self, imag):
        image_resize = cv2.resize(imag, dsize=(int(self.width * 0.3), int(self.height * 0.3)),
                                  interpolation=cv2.INTER_AREA)
        cv2.imshow('imag', image_resize)

    def close_image_write(self):
        self.cv_in_video.release()
        self.cv_out_video.release()
        cv2.destroyAllWindows()

    def do_overlay(self):

        if self.cv_in_video.isOpened():

            current_frame = 0
            start = time.time()

            # iterates through each frame and adds the timestamp before sending
            # the frame to the output file.

            prev_frame = -1
            while current_frame < self.total_frames:

                print('frame number', current_frame)
                image, elapsed_time, current_frame = self.get_frame_image()
                # if prev_frame == current_frame:
                #     break
                prev_frame = current_frame

                if image is not None:

                    timestamp = self.initial_time + dt.timedelta(microseconds=elapsed_time * 1000)

                    image_with_date = self.insert_date(image, timestamp.strftime("%Y-%m-%d %H:%M:%S"))

                    if self.crop_video:
                        image_with_date = image_with_date[int(self.height / 4):int(self.height * 3 / 4),
                                         int(self.width / 4):int(self.width * 3 / 4)]

                    self.set_frame_image(image_with_date)

                    self.show_frame_image(image_with_date)

                    if cv2.waitKey(1) == 27:
                        self.close_image_write()
                        sys.exit()

            self.close_image_write()

            duration = (time.time() - float(start)) / 60

            print("Video has been timestamped")
            print('This video took:' + str(duration) + ' minutes')
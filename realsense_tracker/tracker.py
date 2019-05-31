import cv2
import numpy as np
from realsense_tracker.camera import Camera

tnp = Camera.to_numpy

TRACKING_GREEN = {
    "duct_lower": (48, 45, 156),
    "duct_upper": (77, 137, 220),
    "maxime_lower": (75, 34, 75),
    "maxime_upper": (95, 207, 216),
    "udem_lower": (30, 19, 67),
    "udem_upper": (92, 190, 188)
}

TRACKING_YELLOW = {
    "duckie_lower": (9, 72, 180),
    "duckie_upper": (25, 157, 255),
}


def grab_contours(cnts):
    # if the length the contours tuple returned by cv2.findContours
    # is '2' then we are using either OpenCV v2.4, v4-beta, or
    # v4-official
    if len(cnts) == 2:
        cnts = cnts[0]

    # if the length of the contours tuple is '3' then we are using
    # either OpenCV v3, v4-pre, or v4-alpha
    elif len(cnts) == 3:
        cnts = cnts[1]

    # otherwise OpenCV has changed their cv2.findContours return
    # signature yet again and I have no idea WTH is going on
    else:
        raise Exception(("Contours tuple must have length 2 or 3, "
                         "otherwise OpenCV changed their cv2.findContours return "
                         "signature yet again. Refer to OpenCV's documentation "
                         "in that case"))

    # return the actual contours array
    return cnts


class Tracker(object):

    def __init__(self, color_lower, color_upper):
        self.lower = color_lower
        self.upper = color_upper

    def blur_img(self, frame):
        blurred = cv2.GaussianBlur(frame, (15, 15), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        return hsv

    def prep_image(self, hsv):
        mask = cv2.inRange(hsv, self.lower, self.upper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        return mask

    def track(self, mask):
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        cnts = grab_contours(cnts)

        # only proceed if at least one contour was found
        if len(cnts) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            return center, radius, x, y

        return None, None, None, None

    def get_frame_and_track(self, cam):
        frame = tnp(cam.get_color())[:, :, ::-1]  # RGB to BGR for cv2
        hsv = self.blur_img(frame)
        mask = self.prep_image(hsv)

        # center of mass, radius of enclosing circle, x/y of enclosing circle
        return frame, self.track(mask)

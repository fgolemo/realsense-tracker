import numpy as np
import cv2
import pyrealsense2 as rs
from collections import deque

pipeline = rs.pipeline()

config = rs.config()

# config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 60)
config.enable_stream(rs.stream.color, 640, 480, rs.format.rgb8, 60)

# Start streaming
profile = pipeline.start(config)
s_rgb = profile.get_device().query_sensors()[1]
# s_depth = profile.get_device().query_sensors()[1]

for s in [s_rgb]:
    s.set_option(rs.option.exposure, 50)
    s.set_option(rs.option.enable_auto_exposure, 0)

# greenLower = (54, 70, 50)
# greenUpper = (71, 160, 220)

greenLower = (75, 34, 75)
greenUpper = (95, 207, 216)

duckieLower = (9, 72, 180)
duckieUpper = (25, 157, 255)

redLower = (0,0,0)
redUpper = (0,0,0)

pts = deque(maxlen=32) # keep last couple frames buffered

def noop(value):
    pass

def setup_trackbars(range_filter="HSV"):
    cv2.namedWindow("Trackbars", 0)

    for i in ["MIN", "MAX"]:
        v = 0 if i == "MIN" else 255

        for j in range_filter:
            cv2.createTrackbar("%s_%s" % (j, i), "Trackbars", v, 255, noop)

def get_trackbar_values(range_filter="HSV"):
    values = []

    for i in ["MIN", "MAX"]:
        for j in range_filter:
            v = cv2.getTrackbarPos("%s_%s" % (j, i), "Trackbars")
            values.append(v)

    return values

setup_trackbars()

err = 0
while True:
    frames = pipeline.wait_for_frames()
    color = frames.get_color_frame()
    if not color:
        err += 1
        continue
    # cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
    # cv2.imshow('RealSense', )
    # cv2.waitKey(1)

    frame = np.asanyarray(color.get_data())[:,:,::-1] # RGB to BGR for cv2
    blurred = cv2.GaussianBlur(frame, (15, 15), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    # construct a mask for the color "green", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    # mask = cv2.inRange(hsv, greenLower, greenUpper)


    cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)

    cv2.imshow('RealSense', blurred)
    v1_min, v2_min, v3_min, v1_max, v2_max, v3_max = get_trackbar_values()

    mask = cv2.inRange(hsv, (v1_min, v2_min, v3_min), (v1_max, v2_max, v3_max))
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
        # preview = cv2.bitwise_and(image, image, mask=thresh)
    cv2.imshow("Thresh", mask)

    key = cv2.waitKey(1) & 0xFF

    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break


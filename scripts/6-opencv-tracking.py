import time

import numpy as np
import cv2

from collections import deque

from realsense_tracker.camera import Camera
from realsense_tracker.tracker import Tracker
from realsense_tracker.utils import add_text

cam = Camera(color=True)
tnp = Camera.to_numpy

tracker = Tracker((54, 68, 11), (92, 255, 224))

pts = deque(maxlen=32)  # keep last couple frames buffered

fps = deque(maxlen=100)

while True:
    start = time.time()
    frame = tnp(cam.get_color())[:, :, ::-1]  # RGB to BGR for cv2

    mask = tracker.prep_image(frame)
    frame2 = np.ascontiguousarray(frame, dtype=np.uint8)

    # center of mass, radius of enclosing circle, x/y of enclosing circle
    center, radius, x, y = tracker.track(mask)

    if center is not None and radius > 10:
        # circle center
        cv2.circle(frame2, (int(x), int(y)), int(radius), (0, 255, 255), 2)

        # center of mass
        cv2.circle(frame2, center, 5, (0, 0, 255), -1)

        # update the points queue
        pts.appendleft(center)

    # loop over the set of tracked points
    for i in range(1, len(pts)):
        # if either of the tracked points are None, ignore
        # them
        if pts[i - 1] is None or pts[i] is None:
            continue

        # otherwise, compute the thickness of the line and
        # draw the connecting lines
        thickness = int(np.sqrt(32 / float(i + 1)) * 2.5)
        cv2.line(frame2, pts[i - 1], pts[i], (0, 0, 255), thickness)

    # show the frame to our screen
    diff = time.time()-start

    fps.appendleft(1/diff)
    fps_current = np.around(sum(fps)/len(fps),1)
    add_text(frame2, "fps: {}Hz".format(fps_current))

    cv2.imshow("Frame", frame2)
    cv2.imshow("Thresh", mask)

    key = cv2.waitKey(1) & 0xFF

    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break

# max forward   posx: 0.224 posy: 0.102,    [1, -1, 0, 0]
# max backward  posx: -0.148 posy: 0.016,   [-1, -1, 0, 0]
# max up        posx: 0.013	posy: 0.25,     [.1, -1, -.1, 0]

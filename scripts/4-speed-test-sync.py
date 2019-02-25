import time
import numpy as np

import pyrealsense2 as rs

pipeline = rs.pipeline()

config = rs.config()

config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 60)
config.enable_stream(rs.stream.color, 640, 480, rs.format.rgb8, 60)

# Start streaming
profile = pipeline.start(config)
s_rgb = profile.get_device().query_sensors()[0]
s_depth = profile.get_device().query_sensors()[1]

for s in [s_rgb]:
    s.set_option(rs.option.exposure, 50)
    s.set_option(rs.option.enable_auto_exposure, 0)

tests = 100
err = 0

start = time.time()
for i in range(tests):
    frames = pipeline.wait_for_frames()
    depth = frames.get_depth_frame()
    color = frames.get_color_frame()
    if not color or not depth:
        err += 1
        continue

diff = (time.time() - start) / tests

import matplotlib.pyplot as plt

x, axarr = plt.subplots(3, sharex=True, figsize=(10, 20))

depth = np.asanyarray(depth.get_data())
color = np.asanyarray(color.get_data())
color2 = np.copy(color)

print(depth.shape, color.shape)

color[:, :, 0][depth > 600] = 0
color[:, :, 1][depth > 600] = 0
color[:, :, 2][depth > 600] = 0

color[:, :, 0][depth < 1] = 255
color[:, :, 1][depth < 1] = 255
color[:, :, 2][depth < 1] = 255


axarr[0].imshow(depth)
axarr[1].imshow(color)
axarr[2].imshow(color2)

plt.show()

print("Avg {}s per frame, i.e. {}Hz, tested on {} frames. {} incomplete frames".format(np.around(diff, 4),
                                                                                       np.around(1 / diff, 4), tests,
                                                                                       err))
pipeline.stop()

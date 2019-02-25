import time
import numpy as np

import pyrealsense2 as rs

pipeline = rs.pipeline()

config = rs.config()

config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 60)
# config.enable_stream(rs.stream.color, 640, 480, rs.format.rgb8, 60)

# Start streaming
profile = pipeline.start(config)
s = profile.get_device().query_sensors()[0]
print(dir(s))
print(s.profiles)
print(s.is_depth_sensor())
# print(s.get_option_value_description(rs.option.exposure, 8400))

for attr, value in rs.option.__dict__.items():
    if "__" not in attr:
        try:
            print(attr, "---",
                  s.get_option_description(value), "---",
                  s.get_option(value), "---",
                  s.get_option_range(value))
        except Exception as e:
            # print(e)
            pass

s.set_option(rs.option.exposure, 50)
s.set_option(rs.option.enable_auto_exposure, 0)

tests = 100

start = time.time()
for i in range(tests):
    frames = pipeline.wait_for_frames()
    # depth = frames.get_depth_frame() # Avg 0.0119s per frame, i.e. 83.9805Hz
    # if not depth: continue
    color = frames.get_depth_frame()
    if not color: continue

    # depth.get_distance(x, y)

diff = (time.time() - start) / tests

import matplotlib.pyplot as plt

plt.imshow(np.asanyarray(color.get_data()))
plt.show()

print("Avg {}s per frame, i.e. {}Hz, tested on {} frames".format(np.around(diff, 4), np.around(1 / diff, 4), tests))
pipeline.stop()

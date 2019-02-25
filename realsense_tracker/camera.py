import pyrealsense2 as rs
import numpy as np

class Camera(object):

    def __init__(self, color=True, depth=False):
        assert color or depth

        self.color = color
        self.depth = depth
        self.err = 0

        self.pipeline = rs.pipeline()
        config = rs.config()

        if depth:
            config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 60)
        if color:
            config.enable_stream(rs.stream.color, 640, 480, rs.format.rgb8, 60)

        profile = self.pipeline.start(config)

        if color:
            s_rgb = profile.get_device().query_sensors()[1]

            for s in [s_rgb]:
                s.set_option(rs.option.exposure, 50)
                s.set_option(rs.option.enable_auto_exposure, 0)
                s.set_option(rs.option.gain, 128)
                s.set_option(rs.option.gamma, 470)
                s.set_option(rs.option.saturation, 64)
                s.set_option(rs.option.sharpness, 30)
                s.set_option(rs.option.white_balance, 3200)
                s.set_option(rs.option.enable_auto_white_balance, 0)
                s.set_option(rs.option.backlight_compensation, 0)

    def get_frame(self, fn):
        while True:
            frames = self.pipeline.wait_for_frames()
            color = getattr(frames, fn)()
            if not color:
                self.err += 1
                continue
            else:
                break
        return color

    def get_color(self):
        return self.get_frame("get_color_frame")

    def get_depth(self):
        return self.get_frame("get_depth_frame")

    def get_both(self):
        while True:
            frames = self.pipeline.wait_for_frames()
            color = frames.get_color_frame()
            depth = frames.get_depth_frame()
            if not depth or not color:
                self.err += 1
                continue
            else:
                break
        return color, depth

    @staticmethod
    def to_numpy(frame):
        return np.asanyarray(frame.get_data())
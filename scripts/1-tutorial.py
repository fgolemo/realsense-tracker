import pyrealsense2 as rs
from curses import wrapper

def main(stdscr):
    # Clear screen
    stdscr.clear()

    # Create a context object. This object owns the handles to all connected realsense devices
    pipeline = rs.pipeline()
    pipeline.start()

    while True:
        # This call waits until a new coherent set of frames is available on a device
        # Calls to get_frame_data(...) and get_frame_timestamp(...) on a device will return stable values until wait_for_frames(...) is called
        frames = pipeline.wait_for_frames()
        depth = frames.get_depth_frame()
        if not depth: continue

        coverage = [0] * 64
        y_cnt = 0
        for y in range(480):
            for x in range(640):
                dist = depth.get_distance(x, y)
                if 0 < dist and dist < 1:
                    coverage[x // 10] += 1

            if y % 20 is 19:
                line = ""
                for c in coverage:
                    line += " .:nhBXWW"[c // 25]
                coverage = [0] * 64
                stdscr.addstr(y_cnt, 0, line)
                y_cnt += 1

            stdscr.refresh()
    stdscr.getkey()

wrapper(main)






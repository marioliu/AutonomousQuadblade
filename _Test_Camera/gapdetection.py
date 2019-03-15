import logging
logging.basicConfig(level=logging.INFO)

import time
import numpy as np
import cv2
import pyrealsense as pyrs

# address of the other opencv haar cascades: /usr/share/opencv/haarcascades

with pyrs.Service() as serv:
    with serv.Device() as dev:

        dev.apply_ivcam_preset(0)

        cnt = 0
        last = time.time()
        smoothing = 0.9
        fps_smooth = 30

        height = 480
        width = 640

        times = []
        sample_rate = 0.2
        print('Sample rate: ' + str(sample_rate * 100) + '%')

        while True:
            t1 = time.time()
            cnt += 1
            if (cnt % 10) == 0:
                now = time.time()
                dt = now - last
                fps = 10/dt
                fps_smooth = (fps_smooth * smoothing) + (fps * (1.0-smoothing))
                last = now

            dev.wait_for_frames()

            # color
            c = dev.color
            c = cv2.cvtColor(c, cv2.COLOR_RGB2BGR)

            # detect gap
            # depth is in mm
            depth = dev.depth
            
            sample = [[0.0 for x in range(width)] for _ in range(height)]
            for x in range(width):
                for y in range(height):
                    if (y*width + x) % round(1/sample_rate) == 0:
                        sample[y][x] = depth[y][x]

            # sample
            d = np.array(sample) * dev.depth_scale * 1000
            d = cv2.applyColorMap(d.astype(np.uint8), cv2.COLORMAP_RAINBOW)

            # join color and sample
            cd = np.concatenate((c, d), axis=1)

            cv2.putText(cd, str(fps_smooth)[:4], (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0))

            cv2.imshow('', cd)

            t2 = time.time()
            # times.append(t2 - t1)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                print(times)
                break
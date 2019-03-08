import logging
logging.basicConfig(level=logging.INFO)

import time
import numpy as np
import cv2
import pyrealsense as pyrs

box_cascade = cv2.CascadeClassifier('/home/intelaero/pyrealsense/Haar_training/cascade_big_computer.xml')

with pyrs.Service() as serv:
    with serv.Device() as dev:

        dev.apply_ivcam_preset(0)

        cnt = 0
        last = time.time()
        smoothing = 0.9
        fps_smooth = 30

        while True:

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
            gray = cv2.cvtColor(c, cv2.COLOR_BGR2GRAY)

            # detect box
            boxes = box_cascade.detectMultiScale(c, 1.3, 5)
            for (x,y,w,h) in boxes:
                cv2.rectangle(c,(x,y),(x+w,y+h),(255,0,0),2)
                roi_gray = gray[y:y+h, x:x+w]
                roi_color = c[y:y+h, x:x+w]

                # find distance to center
                cx = int(round(x+(w/2)))
                cy = int(round(y+(h/2)))
                depth = dev.depth[cy][cx]

                print("Box found at distance: " + str(depth/10.0) + " cm")

            # depth
            d = dev.depth * dev.depth_scale * 1000
            d = cv2.applyColorMap(d.astype(np.uint8), cv2.COLORMAP_RAINBOW)

            # join color and depth
            cd = np.concatenate((c, d), axis=1)

            cv2.putText(cd, str(fps_smooth)[:4], (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0))

            cv2.imshow('', cd)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
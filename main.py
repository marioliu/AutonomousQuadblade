'''
Author: Mario Liu
Description: Module to bring together and test all other modules.
'''

from Camera import camera
from Algorithms import create_samples as cs
from Algorithms import adaptive_grid_sizing as ags
from Algorithms import rbf_interpolation as rbfi
from Algorithms import nav as n
from process_frames import plot2
import matplotlib.pyplot as plt
import time

def main():
    cam = camera.Camera()
    cam.connect()
    source = cam
    print('Connected to R200 camera')
    
    max_depth = 4.0
    numFrames = 1
    # height_ratio of 1 keeps all rows of original image
    # default of h_r = 0.5, s_s = 0.3
    height_ratio = 0.5
    sub_sample = 0.3
    # reduce_to argument can be: 'lower', 'middle_lower', 'middle', 'middle_upper', and 'upper'
    reduce_to = 'middle'
    perc_samples = 0.01
    sigma = 0.2
    iters = 2
    min_dist = 1.0
    debug = False

    print('Program settings:')
    print('\tsource: ' + str(source))
    print('\tmax_depth: ' + str(max_depth))
    print('\tnumFrames: ' + str(numFrames))
    print('\theight_ratio: ' + str(height_ratio))
    print('\tsub_sample: ' + str(sub_sample))
    print('\treduce_to: ' + reduce_to)
    print('\tperc_samples: ' + str(perc_samples))
    print('\tsigma: ' + str(sigma))
    print('\titers: ' + str(iters))
    print('\tmin_dist: ' + str(min_dist))
    print('\tdebug: ' + str(debug))

    nav = n.Navigation(debug)

    while True:
        t1 = time.time()

        d, c = cam.getFrames(numFrames, rgb=True)
        d_small = cam.reduceFrame(d, height_ratio = height_ratio, sub_sample = sub_sample, reduce_to = reduce_to)

        adapted = nav.reconstructFrame(d_small, perc_samples, sigma, iters)
        pos = nav.obstacleAvoid(adapted, min_dist)

        if pos == None:
            pos = int(len(d_small[0]) / 2)

        frac = pos/float(len(d_small[0]))
        print('pos = {0}, frac = {1}'.format(pos, frac))

        t2 = time.time()

        print('Time for 1 iter: {0}'.format(t2 -t1))
        print()
        time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        plt.close('all')
        print('\nCtrl-C was pressed, exiting...')
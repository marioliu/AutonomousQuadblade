###############################################################################
#################### Run in opencv_workspace folder
###############################################################################

import cv2
import numpy as np
import os
import time
import subprocess

def create_pos_n_neg_desc():
    for file_type in ['Negative_Images/negatives']:
        
        for img in os.listdir(file_type):

            if file_type == 'pos':
                line = file_type+'/'+img+' 1 0 0 50 50\n'
                with open('info.dat','a') as f:
                    f.write(line)
            elif file_type == 'Negative_Images/negatives':
                line = file_type+'/'+img+'\n'
                with open('bg.txt','a') as f:
                    f.write(line)

def create_samples():
    start = round(time.time())
    print("Start time is: " + str(start) + '\n')

    for i in range(1,89):
        print('\nProcessing box: ' + str(i) + '...')

        # create sample images
        command = 'opencv_createsamples -img ./Positive_Images/box' + str(i) + '.png -bg bg.txt -info info/info' + str(i) + '.lst -pngoutput info -maxxangle 0.5 -maxyangle 0.5 -maxzangle 0.5 -num 3000'

        res = ""
        try:
            split_command = command.split()
            res = subprocess.check_output(split_command)
        
        except:
            pass
    
        for line in res.splitlines():
            print(line)

        #######################################################################

        # create .vec files
        command = 'opencv_createsamples -info info/info' + str(i) + '.lst -num 3000 -w 20 -h 20 -vec samples/positives' + str(i) + '.vec'

        res = ""
        try:
            split_command = command.split()
            res = subprocess.check_output(split_command)
        
        except:
            pass
    
        for line in res.splitlines():
            print(line)

    end = round(time.time())
    print('Time to finish: ' + str(((end-start))/60) + ' minutes')

def main():
    create_samples()

if __name__ == '__main__':
    main()
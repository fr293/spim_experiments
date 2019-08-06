# threaded version of the brightfield controller
# this has support for independent timed operation of the camera and magnet functions

import threading
import Queue
import time
import csv
import numpy as np
import imageio
import spimm as s
from tqdm import tqdm
import cv2
import matplotlib.pyplot as plt
import PySpin



def multiframe(number_of_frames, period, collated_filepath, collated_filename):

    pic_list = Queue.Queue()
    time_list = Queue.Queue()

    # Retrieve singleton reference to system object
    system = PySpin.System.GetInstance()

    # Get current library version
    version = system.GetLibraryVersion()
    print ('Library version: %d.%d.%d.%d' % (version.major, version.minor, version.type, version.build))

    # Retrieve list of cameras from the system
    cam_list = system.GetCameras()

    num_cameras = cam_list.GetSize()

    cam = cam_list[0]

    s.open_camera(cam)

    cv2.namedWindow('%s' % collated_filename, cv2.WINDOW_NORMAL)

    image=[np.zeros((10,10))]

    def actcam(pic_list, time_list, camera_object):
        exp_frame, pictime = s.takepic(camera_object)
        image[0] = cv2.resize(exp_frame, None, fx=0.25, fy=0.25, interpolation=cv2.INTER_CUBIC)
        pic_list.put(exp_frame)
        time_list.put(pictime)

    for i in tqdm(range(number_of_frames)):
        camera = threading.Thread(name='camera', target=actcam, args=(pic_list, time_list, cam))
        camera.start()
        time.sleep(period)
        camera.join()

        cv2.imshow('%s' % collated_filename, image[0])
        cv2.waitKey(1)
    print(' ')
    cv2.destroyAllWindows()

    s.close_camera(cam)

    cam=None

    # Clear camera list before releasing system
    cam_list.Clear()

    # Release system instance
    system.ReleaseInstance()

    with imageio.get_writer(collated_filepath + collated_filename + '.tiff') as stack:
        with open(collated_filepath + collated_filename + '_time.csv', 'w+') as f:
            writer = csv.writer(f)
            while not pic_list.empty():
                pic = pic_list.get()
                stack.append_data(pic)
            while not time_list.empty():
                timepoint = time_list.get()
                writer.writerow([timepoint])

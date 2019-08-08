import numpy as np
import time
import cv2
import os
import PySpin


def open_camera(cam):
    # Retrieve TL device nodemap and print device information
    nodemap_tldevice = cam.GetTLDeviceNodeMap()

    # Initialize camera
    cam.Init()

    # Retrieve GenICam nodemap
    nodemap = cam.GetNodeMap()

    # In order to access the node entries, they have to be casted to a pointer type (CEnumerationPtr here)
    node_acquisition_mode = PySpin.CEnumerationPtr(nodemap.GetNode('AcquisitionMode'))
    if not PySpin.IsAvailable(node_acquisition_mode) or not PySpin.IsWritable(node_acquisition_mode):
        print 'Unable to set acquisition mode to continuous (enum retrieval). Aborting...'
        return False

    # Retrieve entry node from enumeration node
    node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName('Continuous')
    if not PySpin.IsAvailable(node_acquisition_mode_continuous) or not PySpin.IsReadable(
            node_acquisition_mode_continuous):
        print 'Unable to set acquisition mode to continuous (entry retrieval). Aborting...'
        return False

    # Retrieve integer value from entry node
    acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()

    # Set integer value from entry node as new value of enumeration node
    node_acquisition_mode.SetIntValue(acquisition_mode_continuous)

    print 'Acquisition mode set to continuous...'

    cam.BeginAcquisition()

    node_device_serial_number = PySpin.CStringPtr(nodemap_tldevice.GetNode('DeviceSerialNumber'))
    if PySpin.IsAvailable(node_device_serial_number) and PySpin.IsReadable(node_device_serial_number):
        device_serial_number = node_device_serial_number.GetValue()
        print 'Device serial number retrieved as %s...' % device_serial_number

    # vimba_cam = Vimba()
    # vimba_cam.startup()
    # camera_ids = vimba_cam.getCameraIds()
    # camera_object = vimba_cam.getCamera(camera_ids[0])
    # camera_object.openCamera()
    # frame0 = camera_object.getFrame()
    # frame0.announceFrame()
    return cam


def set_exposure(cam, t):
    if cam.ExposureTime.GetAccessMode() != PySpin.RW:
        print ('Unable to set exposure time. Aborting...')
        return False

    # Ensure desired exposure time does not exceed the maximum
    exposure_time_to_set = t

    exposure_time_to_set = min(cam.ExposureTime.GetMax(), exposure_time_to_set)

    cam.ExposureTime.SetValue(exposure_time_to_set)

    print ('Shutter time set to %s us...\n' % exposure_time_to_set)

    # static_write_register = "10000010000000000000"
    # cam1_exp_time_base_no_new = int(np.floor((exposure_time / 0.02)))
    # cam1_exp_time_base_no_new_bin = '{0:012b}'.format(cam1_exp_time_base_no_new)
    # write_register = hex(int(static_write_register + cam1_exp_time_base_no_new_bin, 2))[2:-1]
    # camera_object.writeRegister("F0F0081C", write_register)
    return


def takepic(cam):
    image_result = cam.GetNextImage()

    # camera_object.startCapture()
    # frame0.queueFrameCapture()
    # camera_object.runFeatureCommand('AcquisitionStart')
    pictime = time.time()

    # camera_object.runFeatureCommand('AcquisitionStop')
    # frame0.waitFrameCapture()
    # frame = np.ndarray(buffer=frame0.getBufferByteData(), dtype=np.uint8, shape=(frame0.height, frame0.width))

    image_converted = image_result.Convert(PySpin.PixelFormat_Mono8, PySpin.HQ_LINEAR)
    image_data = image_converted.GetNDArray()
    image_result.Release()

    out_frame = image_data.copy()
    # camera_object.endCapture()
    return out_frame, pictime


def close_camera(cam):
    # plt.close()

    cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Continuous)
    cam.GainAuto.SetValue(PySpin.GainAuto_Continuous)
    cam.EndAcquisition()
    # Deinitialize camera
    cam.DeInit()

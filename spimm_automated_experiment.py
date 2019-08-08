import numpy as np
import spimm_threaded as st
import power_supply_current_controller_threaded as pscct
from pyfiglet import Figlet
import time
import threading
from Tkinter import *
import tkFileDialog


def function(mode=1, params=None):
    # read in data from input csv, and program experiments

    global file_list
    f = Figlet(font='isometric1')
    print f.renderText('Ferg')
    time.sleep(1)
    g = Figlet(font='isometric3')
    print g.renderText('Labs')
    time.sleep(1)

    print('Welcome to the automated spimm creep test tool.')
    time.sleep(0.5)
    if mode == 1:
        print('please select the file that contains details of the experiments to be run:')

    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    if mode == 1:
        root.filename = tkFileDialog.askopenfilename(initialdir='C:/', title='Select file',
                                                     filetypes=(('csv files', '*.csv'), ('all files', '*.*')))
        print('success: you have selected ' + root.filename)
        file_array = np.genfromtxt(root.filename, dtype=None, skip_header=1, delimiter=',', encoding=None)
        file_list = file_array.tolist()

    if mode == 2:
        file_list = params

    print('please select the folder that you want the raw data to be saved in:')

    root.directory = tkFileDialog.askdirectory()
    output_folder = root.directory + '/'
    print('success: you have selected ' + output_folder)

    print('success: starting experiment')

    for experiment_run in file_list:
        # extract current configurations
        [filename, ca, cc, fon, fdur, num_frames, frame_period, temp] = experiment_run
        c_thread = threading.Thread(name='m_thread', target=st.multiframe,
                                    args=(num_frames, frame_period, output_folder, filename))
        m_thread = threading.Thread(name='c_thread', target=pscct.time_currents, args=(cc, ca, fon, fdur))
        print('performing experiment: ' + filename)
        c_thread.start()
        m_thread.start()
        c_thread.join()
        m_thread.join()
    root.destroy()


def main():
    result = True
    function()
    return result


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-

import time
import datetime
import sys
import csv
import argparse

import matplotlib.pyplot as plt

from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_laser_range_finder_v2 import BrickletLaserRangeFinderV2

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 4223
DEFAULT_UID_IN = "Z2m"
DEFAULT_UID_OUT = "Z2q"
DEFAULT_Y_LABLE = 'Axle Count'
DEFAULT_DPI = 1200
DEFAULT_FORMAT_PLOT = 'png'
DEFAULT_FORMAT_DATA = 'csv'
DEFAULT_RECORD = '00'
DEFAULT_FOLDER = 'data'
DEFAULT_FILE_NAME = 'record'
DEFAULT_FLAG = 'w'
DEFAULT_JITTER = 10

DEFAULT_THRESHOLD = 15
DEFAULT_DELAY = 50
DEFAULT_INTERVAL_MIN = 1
DEFAULT_INTERVAL_MAX = 50
DEFAULT_COMPARE_FLAG = 'x'
ONLY_CHANGED_VALUES = False

class DataLogger():

    def __init__(
            self, threshold=DEFAULT_THRESHOLD, delay=DEFAULT_DELAY, interval_min=DEFAULT_INTERVAL_MIN,
            interval_max=DEFAULT_INTERVAL_MAX, compare_flag=DEFAULT_COMPARE_FLAG, only_changed_values=ONLY_CHANGED_VALUES):
        self._data = []
        self._ipconn = IPConnection()
        self._laser_range_finder = []
        self._threshold = threshold
        self._delay = delay
        self._interval_min = interval_min
        self._interval_max = interval_max
        self._compare_flag = compare_flag
        self._only_changed_values = only_changed_values

    def get_data(self):
        return self._data

    def _create_callback(self, device=None):

        if not device in ['IN', 'OUT']:
            raise ValueError('no device selected')

        def _get_distance(distance):
            ct = ct = datetime.datetime.now()
            wheel = 1 if distance <= self._threshold else 0
            self._data.append((ct, device, distance, wheel))
        
        return _get_distance

    def _connect_2_laser_range_finder(self, uids=[DEFAULT_UID_IN, DEFAULT_UID_OUT], host=DEFAULT_HOST, port=DEFAULT_PORT):
        if len(uids) != 2:
            raise ValueError('uids must be defined for (1) IN and (1) OUT')
        for uid in uids:
            self._laser_range_finder.append(BrickletLaserRangeFinderV2(uid, self._ipconn))
        self._ipconn.connect(host, port)
        for device in self._laser_range_finder:
            device.set_enable(True)
        time.sleep(0.25)

    def _disconnect_laser_range_finder(self):
        for device in self._laser_range_finder:
            device.set_enable(False)
        self._laser_range_finder = []
        self._ipconn.disconnect()

    def _register_callback(self, device=None, callback=None):
        if len(self._laser_range_finder) != 2:
            raise IndexError('no device connected')
        if not callable(callback):
            raise ValueError('callback must be a function')
        if device == 'IN':
            self._laser_range_finder[0].register_callback(self._laser_range_finder[0].CALLBACK_DISTANCE, callback)
            self._laser_range_finder[0].set_distance_callback_configuration(
                self._delay, self._only_changed_values, self._compare_flag, self._interval_min, self._interval_max)
            return
        if device == 'OUT':
            self._laser_range_finder[1].register_callback(self._laser_range_finder[1].CALLBACK_DISTANCE, callback)
            self._laser_range_finder[1].set_distance_callback_configuration(
                self._delay, self._only_changed_values, self._compare_flag, self._interval_min, self._interval_max)
            return
        raise ValueError('select IN or OUT device')
    
    def smoothing(self, file_name=DEFAULT_FILE_NAME, filter_type=None, record=DEFAULT_RECORD, format=DEFAULT_FORMAT_DATA, jitter=DEFAULT_JITTER):
        count = 0
        with open('data/' + file_name + '_' + filter_type + '_' + record + '.' + format, 'r') as input_file:
            rows = csv.reader(input_file, delimiter=',')
            last = 0
            current_jitter = jitter
            for row in rows:
                current = int(row[3].strip())
                if last == 1 and current == 1:
                        current_jitter += 1
                if current_jitter >= jitter:
                    current_jitter = 0
                    count += 1
                last = current
        return count

    def log_data_set(self, file_name=DEFAULT_FILE_NAME, device_filter=None, record=DEFAULT_RECORD, format=DEFAULT_FORMAT_DATA, flag=DEFAULT_FLAG):
        with open(DEFAULT_FOLDER + "/" + file_name + "_" + device_filter + "_" + record + "." + DEFAULT_FORMAT_DATA, flag) as f:
            data = self._data
            if device_filter in ['IN', 'OUT']:
                data = filter(lambda x: x[1] == device_filter, self._data)
            for d in data:
                f.write(str(d[0]) + ', ' + str(d[1]) + ', ' + str(d[2]) + ', ' + str(d[3]) + '\n')

    def plot_data_set(self, file_name=DEFAULT_FILE_NAME, device_filter=None, record=DEFAULT_RECORD, format=DEFAULT_FORMAT_PLOT, dpi=DEFAULT_DPI):
        data = self._data
        if device_filter in ['IN', 'OUT']:
            data = filter(lambda x: x[1] == device_filter, self._data)
        prepared_data = [(x[2], x[3]) for x in data]
        plt.clf()
        plt.plot(prepared_data)
        plt.ylabel(DEFAULT_Y_LABLE)
        plt.savefig(DEFAULT_FOLDER + "/" + file_name + "_" + device_filter + "_" + record + "." + format, format=format, dpi=dpi)

    def run(self, file_name=DEFAULT_FILE_NAME, record=DEFAULT_RECORD, jitter=DEFAULT_JITTER, uids=[DEFAULT_UID_IN, DEFAULT_UID_OUT], host=DEFAULT_HOST, port=DEFAULT_PORT):
        self._connect_2_laser_range_finder(uids, host, port)
        self._register_callback('IN', self._create_callback(device='IN'))
        self._register_callback('OUT', self._create_callback(device='OUT'))

        input("Press key to exit\n")

        self._disconnect_laser_range_finder()

        self.log_data_set(file_name, 'IN', record)
        self.log_data_set(file_name, 'OUT', record)
        self.plot_data_set(file_name, 'IN', record)
        self.plot_data_set(file_name, 'OUT', record)

        data = []
        data.append(self.smoothing(file_name, 'IN', record, jitter=jitter))
        data.append(self.smoothing(file_name, 'OUT', record, jitter=jitter))
        print(data)

def args_setup():
    parser = argparse.ArgumentParser(prog='DataLogger', description='Data logger which logs the incoming data of two laser range finder.', epilog='Here comes the Bahn!')
    parser.add_argument('-f', help='file name', default=DEFAULT_FILE_NAME)
    parser.add_argument('-r', help='record', default=DEFAULT_RECORD)
    parser.add_argument('-t', help='threshold', default=DEFAULT_THRESHOLD)
    parser.add_argument('-d', help='delay', default=DEFAULT_DELAY)
    parser.add_argument('-a', help='min', default=DEFAULT_INTERVAL_MIN)
    parser.add_argument('-b', help='max', default=DEFAULT_INTERVAL_MAX)
    parser.add_argument('-j', help='jitter', default=DEFAULT_JITTER)
    return parser.parse_args()

def main():
    args = args_setup()
    print(args.f, args.r)
    data_logger = DataLogger(threshold=args.t, delay=args.d, interval_min=args.a, interval_max=args.b)
    data_logger.run(file_name=args.f, record=args.r, jitter=int(args.j))
    
if __name__ == "__main__":
    main()

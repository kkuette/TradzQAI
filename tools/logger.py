import time
import os
from threading import Thread

class Logger(Thread):

    def __init__(self):

        self.path = "logs/"

        self.names = []

        self.logs = {}
        self.id = {}
        self.current_index = {}

        self.log_file_name = {}
        self.log_file = {}
        self.log_path = ""
        self.log_file_path = {}

        self._running = False
        self.event = None

        Thread.__init__(self)

    def setEvent(self, event):
        self.event = event

    def new_logs(self, name):
        '''
        name : log name as string
        '''
        if type(name) is str:
            self.names.append(name)
            self.logs[name] = []
            self.id[name] = -1
            self.current_index[name] = -1
            self.log_file_path[name] = self.log_path + self.check_log_file(name)
            self.log_file[name] = None
        else:
            raise ValueError("name should be a string")

    def set_log_path(self, base_path):
        self.log_path = base_path + self.path
        self.check_log_dir()

    def _add(self, log, name):
        self.id[name] += 1
        self.logs[name].append(time.strftime("%Y:%m:%d %H:%M:%S") + \
            " " + '{:06d}'.format(self.id[name]) + " " + str(log) + "\n")

    def check_log_dir(self):
        if not os.path.exists(self.log_path):
            os.mkdir(self.log_path)

    def check_log_file(self, log_name):
        cdir = os.listdir(self.log_path)
        for d in cdir:
            if time.strftime("%Y_%m_%d") in d and log_name == d.split('_')[0]:
                return d
        return log_name + "_" + time.strftime("%Y_%m_%d") + ".txt"

    def load_log(self, log_name):
        self.log_file_name[log_name] = self.check_log_file(log_name)
        self.log_file_path[log_name] = self.log_path + "/" + self.log_file_name[log_name]
        self.log_file[log_name] = open(self.log_file_path[log_name], 'a')

    def save_logs(self, logs=None, name=None):
        self.log_file[name] = open(self.log_file_path[name], 'a')
        self.log_file[name].write(logs)
        self.log_file[name].close()

    def write_logs(self):
        for name in self.names:
            if self.current_index[name] < self.id[name]:
                while self.current_index[name] < self.id[name]:
                    self.current_index[name] += 1
                    self.save_logs(logs=self.logs[name][self.current_index[name]], name=name)

    def stop(self):
        self.running = False

    def run(self, write_time=1):
        self.running = True
        while self.running:
            self.write_logs()
            if self.event:
                self.event.wait(timeout=write_time)
        self.write_logs()

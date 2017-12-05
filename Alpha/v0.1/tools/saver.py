import os
import time

class saver():

    def __init__(self):
        self.root_path = "./save/"
        self.path = ""

        self.log_file_name = ""
        self.model_file_name = ""

        self.log_file = None

    def check_save_dir(self):
        if os.path.exists(self.root_path) is False:
            os.mkdir(self.path)

    def check_model_dir(self, name):
        self.path = self.root_path + name + "/"
        if os.path.exists(self.path) is False:
            os.mkdir(self.path)
        else:
            self.model_file_name = self.check_model_file()

    def check_log_dir(self, log_path):
        if os.path.exists(self.path + log_path) is False:
            os.mkdir(self.path + log_path)
            self.log_file_name = "_log" + time.strftime("_%Y_%m_%d") + ".txt"
        else:
            self.log_file_name = self.check_log_file(log_path)

    def check_model_file(self):
        cdir = os.listdir(self.path)
        cdir = cdir.sort()
        for d in cdir:
            if "_model" in d:
                return d
        return None

    def check_log_file(self, log_path):
        cdir = os.listdir(self.path + log_path)
        cdir = cdir.sort()
        for d in cdir:
            if "_log" in d and time.strftime("%Y_%m_%d") in d:
                return d
        return "_log" + time.strftime("_%Y_%m_%d") + ".txt"

    def _check(self, name, log_path):
        self.check_save_dir()
        self.check_model_dir(name)
        self.check_log_dir(log_path)

    def _load(self):
        self.log_file = open(self.log_file_name, 'a')

    def _save(self, logs):
        self.log_file.write(logs)

    def _end(self, logs):
        self.log_file.write(logs)
        self.log_file.close()

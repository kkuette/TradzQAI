import os
import time
import json
from sortedcontainers import SortedDict
from deepdiff import DeepDiff

class Saver(object):

    def __init__(self):

        self.root_path = "save/"

        self.name = os.path.basename(__file__).replace(".py", "")

        self.model_file_name = ""
        self.model_file_path = ""

        self.network_file_name = "network.json"
        self.network_file = None
        self.network_file_path = ""

        self.agent_file_name = "agent.json"
        self.agent_file = None
        self.agent_file_path = ""

        self.env_file_name = "environnement.json"
        self.env_file = None
        self.env_file_path = ""

        self.training_in_data_file_name = "train_in.txt"
        self.training_out_data_file_name = "train_out.txt"
        self.training_in_data_file = None
        self.training_out_data_file = None
        self.training_data_path = "training_data/"

        self.dir_id = 0

        self.model_directory = ""

        self.files_checked = False

    def get_model_dir(self):
        return self.model_directory

    def check_save_dir(self):
        if not os.path.exists(self.root_path):
            os.mkdir(self.root_path)

    def check_model_dir(self, model_name):
        self.path = self.root_path + model_name + "/"
        self.model_directory = self.root_path + model_name
        if not os.path.exists(self.path):
            os.mkdir(self.path)

    def check_training_data_dir(self):
        self.training_data_path = "training_data/"
        tmp_path = self.path + self.training_data_path
        if not os.path.exists(tmp_path):
            os.mkdir(tmp_path)
        self.training_data_path = tmp_path

    def check_settings_files(self, directory):
        if not 'config'in directory:
            directory += 'config/'
        if not os.path.exists(directory):
            return False
        cdir = os.listdir(directory)
        files = 0
        for d in cdir:
            if self.network_file_name in d or \
                self.agent_file_name in d or \
                self.env_file_name in d:
                files += 1
        if files == 3:
            return True
        else:
            return False

    def check_settings(self, env, agent, network):
        if self.check_settings_files(self.model_directory+"/"):
            _env, _agent, _network = self.load_settings(self.model_directory+"/")
            if DeepDiff(_env, env) == {} and \
                DeepDiff(_agent, agent) == {} and \
                DeepDiff(_network, network) == {}:
                return True
            else:
                return False
        else:
            return True

    def _check(self, model_name, settings, log_path=None):
        self.check_save_dir()
        self.check_model_dir(model_name + "_" + str(self.dir_id))
        #self.check_training_data_dir()
        if not self.check_settings(settings['env'], settings['agent'], settings['network']):
            self.dir_id += 1
            self._check(model_name, settings)
        else:
            self.save_settings(settings['env'], settings['agent'], settings['network'], self.model_directory+"/")
            self.files_checked = True

    def load_settings(self, directory):
        if not 'config'in directory:
            directory += 'config/'
        with open(directory+self.env_file_name, 'r') as fp:
            env = json.load(fp=fp, object_pairs_hook=SortedDict)
        with open(directory+self.agent_file_name, 'r') as fp:
            agent = json.load(fp=fp, object_pairs_hook=SortedDict)
        with open(directory+self.network_file_name, 'r') as fp:
            network = json.load(fp=fp)
        return env, agent, network

    def load_agent_settings(self, directory):
        with open(directory+self.agent_file_name, 'r') as fp:
            agent = json.load(fp=fp, object_pairs_hook=SortedDict)
        return agent

    def load_env_settings(self, directory):
        with open(directory+self.env_file_name, 'r') as fp:
            env = json.load(fp=fp, object_pairs_hook=SortedDict)
        return env

    def load_network_settings(self, directory):
        with open(directory+self.network_file_name, 'r') as fp:
            network = json.load(fp=fp)
        return network

    def _load(self):
        self.training_in_data_file = open(self.training_data_path + "/" + self.training_in_data_file_name, 'a')
        self.training_out_data_file = open(self.training_data_path + "/" + self.training_out_data_file_name, 'a')

    def save_training_data(self, _in, out):
        for v in _in:
            self.training_in_data_file.write(str(v) + "\n")
        for i in out:
            self.training_out_data_file.write(str(i) + "\n")
        self.training_in_data_file.close()
        self.training_out_data_file.close()
        self.training_in_data_file = open(self.training_data_path + "/" + self.training_in_data_file_name, 'a')
        self.training_out_data_file = open(self.training_data_path + "/" + self.training_out_data_file_name, 'a')

    def save_settings(self, env, agent, network, directory):
        if not 'config'in directory:
            directory += 'config/'
        if not os.path.exists(directory):
            os.mkdir(directory)
        with open(directory+self.env_file_name, 'w') as fp:
            json.dump(env, fp, indent=4, sort_keys=True)
        with open(directory+self.agent_file_name, 'w') as fp:
            json.dump(agent, fp, indent=4, sort_keys=True)
        with open(directory+self.network_file_name, 'w') as fp:
            json.dump(network, fp, indent=4, sort_keys=True)

import numpy as np

import tensorflow as tf
import keras
from keras.models import load_model

class DEEP:

    def __init__(self, model_path):
        self.model = load_model(model_path)
        self.graph = tf.get_default_graph()

    def reset(self):
        pass

    def act(self, state, deterministic=False):
        with self.graph.as_default():
            return np.argmax(self.model.predict(state))

    def should_stop(self):
        return False

    def save_model(self, directory=None, append_timestep=False):
        self.model.save(directory)

    def get_specs(env=None):
        specs = dict(type="DEEP")
        return specs

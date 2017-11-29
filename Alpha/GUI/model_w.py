from ttkthemes import themed_tk as tk
import tkinter.ttk

import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import style

from GUI.interface import *
from environnement import *

style.use('ggplot')

class model_window():

    def __init__(self, root, env):
        self.build_model(root)

    def build_model(self, root):
        self.fig = Figure(figsize=(20,20), dpi=200)
        self.a = self.fig.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.fig, root)
        self.canvas.show()
        self.canvas.get_tk_widget().pack()

    def update_graph(self, env):
        self.a.clear()
        if env.cdatai > 40:
            self.a.plot(env.lst_state[env.cdatai-40:env.cdatai])
        else:
            self.a.plot(env.lst_state)
        self.canvas.draw()

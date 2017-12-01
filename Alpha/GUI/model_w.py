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
        self.insigf = ttk.Frame(root)
        self.df = ttk.Frame(root)

        self.fig_insig = Figure(figsize=(20,4), dpi=100)
        self.a_insig = self.fig_insig.add_subplot(111)

        self.fig_d = Figure(figsize=(20,4), dpi=100)
        self.a_d = self.fig_d.add_subplot(111)

        self.canvas_in = FigureCanvasTkAgg(self.fig_insig, root)
        self.canvas_d = FigureCanvasTkAgg(self.fig_d, root)

        self.insigf.pack(side=TOP, fill=BOTH)
        self.df.pack(side=TOP, fill=BOTH)

        self.canvas_d.show()
        self.canvas_in.show()

        self.canvas_d.get_tk_widget().pack(side=TOP, fill=BOTH)
        self.canvas_in.get_tk_widget().pack(side=BOTTOM, fill=BOTH)

    def update_graph(self, env):

        self.a_d.clear()
        self.a_insig.clear()

        if env.cdatai > 40:
            self.a_d.plot(env.lst_data[env.cdatai-40:env.cdatai])
            self.a_insig.plot(env.lst_state[env.cdatai-40:env.cdatai])
        else:
            self.a_d.plot(env.lst_data)
            self.a_insig.plot(env.lst_state)

        self.canvas_in.draw()
        self.canvas_d.draw()

        self.canvas_in.flush_events()
        self.canvas_d.flush_events()

from tkinter import *
import tkinter.ttk as ttk
import RNN
from tkinter.filedialog import *
from tkinter.messagebox import *

class interface(Frame):

    def __init__(self, window, **kwargs):
        self.name = "TradzQAI"
        self.version = "Alpha v0.1"
        window.title(self.name + " " + self.version)
        Frame.__init__(self, window, **kwargs)
        self.pack(fill=BOTH)
        self.text = Text(window, width=100, height=100)
        self.text.insert(INSERT, self.name + " " + self.version)
        self.text.pack()
        self.parsing = Button(self, text="Start parsing", command=quit)
        self.parsing.pack()
        self.run_ai = Button(self, text="Run AI", command=RNN.full_run)
        self.run_ai.pack()

    def text_update(self, state):
        self.text.insert(END, "\n")
        self.text.insert(END, state)
        self.pack()

def launch_interface():
    window = Tk()
    interfaces = interface(window)
    interfaces.mainloop()
    return interfaces

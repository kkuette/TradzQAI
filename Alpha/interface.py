from tkinter import *
from core import *
from parsing import parsing

class interface(Frame):

    def __init__(self, window, **kwargs):
        self.name = "EasyMoney"
        self.version = "v0.0"
        window.title(self.name + " " + self.version)
        Frame.__init__(self, window, **kwargs)
        self.pack(fill=BOTH)
        self.text = Text(window, width=100, height=100)
        self.text.insert(INSERT, self.name + " " + self.version)
        self.text.pack()
        self.parsing = Button(self, text="Start parsing", command=parsing)
        self.parsing.pack()
        self.run_ai = Button(self, text="Run AI", command=run_ai)
        self.run_ai.pack()

    def text_update(self, state):
        self.text.insert(END, "\n")
        self.text.insert(END, state)
        self.pack()

def launch_interface():
    window = Tk()
    interface = interface(window)
    return interface

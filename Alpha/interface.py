from tkinter import *
import tkinter.ttk as ttk

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
        self.parsing = Button(self, text="Start parsing", command=self.set_pause)
        self.parsing.pack()
        self.run_ai = Button(self, text="Run AI", command=quit)
        self.run_ai.pack()
        self.pause = True

    def set_pause(self):
        if self.set_pause is True:
            self.pause = False
        else:
            self.pause = True

    def text_update(self, state):
        self.text.insert(END, "\n")
        self.text.insert(END, state)
        self.pack()

def launch_interface():
    window = Tk()
    interfaces = interface(window)
    interfaces.mainloop()
    return interfaces

launch_interface()

import numpy as np
import pandas as pd

import time, math

# Chekc if it can be converted as float
def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

# Check if the string can be a bool
def str2bool(value):
    if str(value).lower() in ("yes", "y", "true",  "t", "1", "1.0"): return True
    if str(value).lower() in ("no",  "n", "false", "f", "0", "0.0"): return False
    raise Exception('Invalid value for boolean conversion: ' + str(value))

# prints formatted price
def formatPrice(n):
        return "{0:.2f}".format(n) + " €"

# returns the sigmoid
def sigmoid(x):
    try:
        exp = math.exp(-x)
    except:
        exp = float('Inf')
    return 1 / (1 + exp)

def naive(x):
    return x/100

def act_processing(act):
    if act == 1:
        return ([1, 0, 0])
    elif act == 2:
        return ([0, 1, 0])
    else:
        return ([0, 0, 1])

# Some color
def style(s, style):
    return style + s + '\033[0m'


def green(s):
    return style(s, '\033[92m')


def blue(s):
    return style(s, '\033[94m')


def yellow(s):
    return style(s, '\033[93m')


def red(s):
    return style(s, '\033[91m')


def pink(s):
    return style(s, '\033[95m')


def bold(s):
    return style(s, '\033[1m')


def underline(s):
    return style(s, '\033[4m')

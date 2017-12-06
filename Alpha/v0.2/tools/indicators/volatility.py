from tools.indicators.standard_deviation import standard_deviation as sd
from tools.indicators.standard_variance import standard_variance as sv
import numpy as np

np.seterr(divide='ignore', invalid='ignore')

def volatility(data, period):
    """
    Volatility.

    Formula:
    SDt / SVt
    """
    volatility = sd(data, period) / sv(data, period)
    return volatility

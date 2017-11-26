import numpy as np
from indicators.catch_errors import check_for_period_error
from indicators.function_helper import fill_for_noncomputable_vals

np.seterr(divide='ignore', invalid='ignore')

def standard_deviation(data, period):
    """
    Standard Deviation.

    Formula:
    std = sqrt(avg(abs(x - avg(x))^2))
    """
    check_for_period_error(data, period)

    stds = list(map(
        lambda idx:
        np.std(data[idx+1-period:idx+1], ddof=1),
        range(period-1, len(data))
        ))

    stds = fill_for_noncomputable_vals(data, stds)
    return stds

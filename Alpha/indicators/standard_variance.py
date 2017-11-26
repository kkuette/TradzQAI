import numpy as np
from indicators.catch_errors import check_for_period_error
from indicators.function_helper import fill_for_noncomputable_vals

np.seterr(divide='ignore', invalid='ignore')

def standard_variance(data, period):
    """
    Standard Variance.

    Formula:
    (Ct - AVGt)^2 / N
    """
    check_for_period_error(data, period)
    sv = list(map(
        lambda idx:
        np.var(data[idx+1-period:idx+1], ddof=1),
        range(period-1, len(data))
        ))
    sv = fill_for_noncomputable_vals(data, sv)

    return sv

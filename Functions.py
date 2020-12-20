import numpy as np
from decimal import Decimal

def is_divisible(num, divisor):
    a = Decimal(str(num))
    b = Decimal(str(divisor))
    c = a % b
    return c.is_zero()

def h_natural(surf_temp = 0, amb_temp = 0):
        return 1.31e-6 * np.abs(surf_temp - amb_temp) ** (1/3) #working

def h_forced(wind_speed = 0):
    return 11.4 + 5.7 * wind_speed


def Phi_s(surf_temp=0, amb_temp = 20, wind_speed=0, natural=True):
    if natural:
        return h_natural(surf_temp, amb_temp) * (surf_temp - amb_temp)
    else:
        return h_forced(wind_speed) * surf_temp
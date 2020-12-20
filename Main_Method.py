import numpy as np
from decimal import Decimal

def is_divisible(num, divisor):
    a = Decimal(str(num))
    b = Decimal(str(divisor))
    c = a % b
    return c.is_zero()

def H_Natural(surf_temp):
        return  1.31e-6 * np.abs(surf_temp ** 1/3)


def H_Forced(wind_speed):
    return 11.4 + 5.7 * wind_speed


def Phi_s(surf_temp=0, wind_speed=0, natural=True):
    if natural:
        return H_Natural(surf_temp) * surf_temp
    else:
        return H_Forced(wind_speed) * surf_temp


def Neumann_Boundaries(initial_state, h, wind_speed, k, natural=True):
    # setting boundary conditions

    initial_x_dim = np.shape(initial_state)[1]
    initial_y_dim = np.shape(initial_state)[0]

    for y in range(initial_y_dim):
        for x in range(initial_x_dim):
            if natural:

                """Central Difference"""
                # central difference calculated by hand (does not work as the one above does)
                if y == 0:  # bottom
                    surf_temp = initial_state[y+1, x]
                    initial_state[y, x] = initial_state[y+2, x] + 2 * h * (-1 * Phi_s(surf_temp, natural=natural) / k)
                    #initial_state[i, j] = initial_state[i + 2, j] + 2 * hy * (-1 * (Phi_s(surf_temp, natural=natural)) / k)
                if y == initial_y_dim - 1:  # top
                    surf_temp = initial_state[y - 1, x]
                    initial_state[y, x] = initial_state[y-2, x] + 2 * h * (-1 * Phi_s(surf_temp, natural=natural) / k)
                    #initial_state[i, j] = initial_state[i - 2, j] + 2 * hy * (-1 * (Phi_s(surf_temp, natural=natural)) / k)
                if x == 0:  # left
                    surf_temp = initial_state[y, x + 1]
                    initial_state[y, x] = initial_state[y, x+2] + 2 * h * (-1 * Phi_s(surf_temp, natural=natural) / k)
                    #initial_state[i, j] = initial_state[i, j + 2] + 2 * hx * (-1 * (Phi_s(surf_temp, natural=natural)) / k)
                if x == initial_x_dim - 1:  # right
                    surf_temp = initial_state[y, x - 1]
                    initial_state[y, x] = initial_state[y, x-2] + 2 * h * (-1 * Phi_s(surf_temp, natural=natural) / k)
                    #initial_state[i, j] = initial_state[i, j - 2] + 2 * hx * (-1 * (Phi_s(surf_temp, natural=natural)) / k)


            # elif not natural:
            #     if i == 0:  # bottom boundary
            #         surf_temp = initial_state[i + 1, j]
            #         initial_state[i, j] = surf_temp - 2 * hx * H_Forced(wind_speed) * surf_temp
            #     if i == initial_y_dim - 1:  # top boundary
            #         surf_temp = initial_state[i - 1, j]
            #         initial_state[i, j] = surf_temp - 2 * hx * H_Forced(wind_speed) * surf_temp
            #     if j == 0:  # left boundary
            #         surf_temp = initial_state[i, j + 1]
            #         initial_state[i, j] = surf_temp - 2 * hx * H_Forced(wind_speed) * surf_temp
            #     if j == initial_x_dim - 1:  # right boundary
            #         surf_temp = initial_state[i, j - 1]
            #         initial_state[i, j] = surf_temp - 2 * hx * H_Forced(wind_speed) * surf_temp

    return initial_state


def Jacobi_Solve(x_range, y_range, h = 0.1, initial_guess=0, amb_temp = 20, wind_speed = 0, natural=True): #input dimensions in mm
    initial_guess -= amb_temp

    # definitions
    initial_x_dim = int((x_range / h) + 2)
    initial_y_dim = int((y_range / h) + 2)

    initial_state = np.full((initial_y_dim, initial_x_dim), initial_guess)

    # initial boundary conditions
    wind_speed = 30
    k = 150e-3
    q = 0.5
    #q = 0

    #total power
    power = q * x_range * y_range

    for iteration in range(1000):
        final_state = np.zeros((initial_y_dim, initial_x_dim))
        initial_state = Neumann_Boundaries(initial_state, h, wind_speed, k, natural)
        # a = 3 #test
        # solving iteration of Jacobi method
        for y in range(1, initial_y_dim - 1):  # y
            for x in range(1, initial_x_dim - 1):  # x
                s = - q / k
                h2 = np.square(h)
                updated_value = 0.25 * (initial_state[y, x-1] + initial_state[y, x+1] + initial_state[y-1, x] + initial_state[y+1, x] - h2 * s)
                final_state[y, x] = updated_value
                a = 1
        initial_state = final_state
        # pass

    # tidies up array
    final_state = np.delete(final_state, 0, 0)
    final_state = np.delete(final_state, 0, 1)
    final_state = np.delete(final_state, initial_y_dim - 2, 0)
    final_state = np.delete(final_state, initial_x_dim - 2, 1)

    final_state = final_state + amb_temp

    avg_temp = np.average(final_state)
    print()
    print(final_state)
    print(avg_temp)
    return final_state


Jacobi_Solve(14, 1, h = 0.1, initial_guess=10000, amb_temp= 20)


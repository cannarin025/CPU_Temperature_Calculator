import numpy as np
import copy


def H_Natural(surf_temp, amb_temp):
    if surf_temp - amb_temp >= 0:
        return np.abs(1.31 * ((float(surf_temp) - amb_temp) ** (1 / 3)))
    else:
        return -1 * np.abs(1.31 * ((float(surf_temp) - amb_temp) ** (1 / 3)))


def H_Forced(wind_speed):
    return 11.4 + 5.7 * wind_speed


def Phi_s(surf_temp=0, amb_temp=0, wind_speed=0, natural=True):
    if natural:
        return H_Natural(surf_temp, amb_temp) * (surf_temp - amb_temp)
    else:
        return H_Forced(wind_speed) * (surf_temp - amb_temp)


def Neumann_Boundaries(initial_state, hx, hy, amb_temp, wind_speed, k, natural=True):
    # setting boundary conditions

    initial_x_dim = np.shape(initial_state)[1]
    initial_y_dim = np.shape(initial_state)[0]

    #setting outer ghost points to ambient temp
    for y in range(initial_y_dim):
        for x in range(initial_x_dim):
            if y == 0 or x == 0:
                initial_state[y, x] = amb_temp

            if y == initial_y_dim - 1 or x == initial_x_dim - 1:
                initial_state[y, x] = amb_temp

    for y in range(1, initial_y_dim - 1):
        for x in range(1, initial_x_dim - 1):

            if natural:

                """Central Difference"""

                # central difference with boundaries set to Ta.
                if y == 1:  # bottom
                    initial_state[y, x] = (k * (initial_state[y + 1, x] - amb_temp) / (-1.31 * 2 * hy)) ** (3 / 4) + amb_temp
                if y == initial_y_dim - 2:  # top
                    initial_state[y, x] = (k * (amb_temp - initial_state[y - 1, x]) / (-1.31 * 2 * hy)) ** (3 / 4) + amb_temp
                if x == 1:  # left
                    initial_state[y, x] = (k * (initial_state[y, x + 1] - amb_temp) / (-1.31 * 2 * hx)) ** (3 / 4) + amb_temp
                if x == initial_x_dim - 2:  # right
                    initial_state[y, x] = (k * (amb_temp - initial_state[y, x - 1]) / (-1.31 * 2 * hx)) ** (3 / 4) + amb_temp

                """Forward Difference"""

                # if i == 0:                  #bottom boundary
                #     surf_temp = initial_state[i + 1, j]
                #     initial_state[i,j] = surf_temp - (hy * H_Natural(surf_temp, amb_temp) * (surf_temp - amb_temp) / k)
                # if i == initial_y_dim - 1:  #top boundary
                #     surf_temp = initial_state[i - 1, j]
                #     initial_state[i, j] = surf_temp - (hy * H_Natural(surf_temp, amb_temp) * (surf_temp - amb_temp) / k)
                # if j == 0:                  #left boundary
                #     surf_temp = initial_state[i, j + 1]
                #     initial_state[i, j] = surf_temp - (hx * H_Natural(surf_temp, amb_temp) * (surf_temp - amb_temp) / k)
                # if j == initial_x_dim - 1:  #right boundary
                #     surf_temp = initial_state[i, j - 1]
                #     initial_state[i, j] = surf_temp - (hx * H_Natural(surf_temp, amb_temp) * (surf_temp - amb_temp) / k)


            # elif not natural:
            #     if i == 0:  # bottom boundary
            #         surf_temp = initial_state[i + 1, j]
            #         initial_state[i, j] = surf_temp - 2 * hx * H_Forced(wind_speed) * (surf_temp - amb_temp)
            #     if i == initial_y_dim - 1:  # top boundary
            #         surf_temp = initial_state[i - 1, j]
            #         initial_state[i, j] = surf_temp - 2 * hx * H_Forced(wind_speed) * (surf_temp - amb_temp)
            #     if j == 0:  # left boundary
            #         surf_temp = initial_state[i, j + 1]
            #         initial_state[i, j] = surf_temp - 2 * hx * H_Forced(wind_speed) * (surf_temp - amb_temp)
            #     if j == initial_x_dim - 1:  # right boundary
            #         surf_temp = initial_state[i, j - 1]
            #         initial_state[i, j] = surf_temp - 2 * hx * H_Forced(wind_speed) * (surf_temp - amb_temp)

    return initial_state


def Jacobi_Solve(x_range, y_range, x_points=10, y_points=10, initial_guess=0, natural=True):
    # definitions
    hx = x_range / x_points
    hy = y_range / y_points

    initial_x_dim = x_points + 2
    initial_y_dim = y_points + 2
    initial_state = np.full((initial_y_dim, initial_x_dim), initial_guess)

    # initial boundary conditions
    amb_temp = 20
    wind_speed = 30
    k = 150
    # q = 0.5e9
    q = 0

    for iteration in range(10000):
        final_state = np.zeros((initial_y_dim, initial_x_dim))
        initial_state = Neumann_Boundaries(initial_state, hx, hy, amb_temp, wind_speed, k, natural)
        # a = 3 #test
        # solving iteration of Jacobi method
        for y in range(1, initial_y_dim - 1):  # y
            for x in range(1, initial_x_dim - 1):  # x
                s = - q / k
                # updated_value = (((1/(hx**2)) * initial_state[i+1, j]) + ((1/(hx**2)) * initial_state[i-1, j]) + ((1/(hy**2)) * initial_state[i, j-1]) + ((1/(hy**2)) * initial_state[i, j+1]) - s) / ((2/(hx**2)) + (2/(hy**2)))
                c = 1 / (2 * ((hy ** 2) + (hx ** 2)))
                # updated_value = c * (((hy**2) * initial_state[i - 1, j]) + ((hy**2) * initial_state[i + 1, j]) + ((hx**2) * initial_state[i, j + 1]) + ((hx**2) * initial_state[i, j - 1]) - ((hx**2) * (hy**2) * s))
                updated_value = c * (((hx ** 2) * (initial_state[y - 1, x] + initial_state[y + 1, x])) + (
                            (hy ** 2) * (initial_state[y, x - 1] + initial_state[y, x + 1])) - (
                                                 (hy ** 2) * (hx ** 2) * s))
                final_state[y, x] = updated_value
                a = 1
        initial_state = final_state
        # pass

    # tidies up array
    final_state = np.delete(final_state, 0, 0)
    final_state = np.delete(final_state, 0, 1)
    final_state = np.delete(final_state, initial_y_dim - 2, 0)
    final_state = np.delete(final_state, initial_x_dim - 2, 1)

    print()
    print(final_state)
    return final_state


Jacobi_Solve(0.014, 0.002, x_points=10, y_points=10, initial_guess=5)


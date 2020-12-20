import numpy as np
import copy


def H_Natural(surf_temp, amb_temp):
    if surf_temp - amb_temp >= 0:
        return np.abs(1.31 * ((float(surf_temp) - amb_temp) ** (1 / 3)))
    else:
        #return -1 * np.abs(1.31 * ((float(surf_temp) - amb_temp) ** (1 / 3)))
        return np.abs(1.31 * ((float(surf_temp) - amb_temp) ** (1 / 3)))

def H_Forced(wind_speed):
    return 11.4 + 5.7 * wind_speed



def Phi_s(surf_temp = 0, amb_temp = 0, wind_speed = 0, natural = True):
    if natural:
        return H_Natural(surf_temp, amb_temp) * (surf_temp - amb_temp)
    else:
        return H_Forced(wind_speed) * (surf_temp - amb_temp)



def Neumann_Boundaries(initial_state, hx, hy, amb_temp, wind_speed, k, natural=True):
    # setting boundary conditions

    initial_x_dim = np.shape(initial_state)[1]
    initial_y_dim = np.shape(initial_state)[0]

    for i in range(initial_y_dim):
        for j in range(initial_x_dim):
            if natural:

                """Central Difference"""

                # this seems to work. Do not know why.
                # if i == 0:  # bottom boundary
                #     surf_temp = initial_state[i + 1, j]
                #     initial_state[i, j] = initial_state[i + 2, j] - ((2 * hx * H_Natural(surf_temp, amb_temp) * (amb_temp - surf_temp)) / -k)
                # if i == initial_y_dim - 1:  # top boundary
                #     surf_temp = initial_state[i - 1, j]
                #     initial_state[i, j] = initial_state[i - 2, j] - ((2 * hx * H_Natural(surf_temp, amb_temp) * (amb_temp - surf_temp)) / -k)
                # if j == 0:  # left boundary
                #     surf_temp = initial_state[i, j + 1]
                #     initial_state[i, j] = initial_state[i, j + 2] - ((2 * hy * H_Natural(surf_temp, amb_temp) * (amb_temp - surf_temp)) / -k)
                # if j == initial_x_dim - 1:  # right boundary
                #     surf_temp = initial_state[i, j - 1]
                #     initial_state[i, j] = initial_state[i, j - 2] - ((2 * hy * H_Natural(surf_temp, amb_temp) * (amb_temp - surf_temp)) / -k)

                #central difference calculated by hand (does not work as the one above does)
                if i == 0:                  #bottom
                    surf_temp = initial_state[i + 1, j]
                    initial_state[i,j] = initial_state[i + 2, j] + 2 * hy * (-1 * (Phi_s(surf_temp, amb_temp, natural=natural))/k)
                if i == initial_y_dim - 1:  #top
                    surf_temp = initial_state[i - 1, j]
                    initial_state[i,j] = initial_state[i - 2, j] + 2 * hy * (-1 * (Phi_s(surf_temp, amb_temp, natural=natural))/k)
                if j == 0:                  #left
                    surf_temp = initial_state[i, j + 1]
                    initial_state[i,j] = initial_state[i, j + 2] + 2 * hx * (-1 * (Phi_s(surf_temp, amb_temp, natural=natural))/k)
                if j == initial_x_dim - 1:  #right
                    surf_temp = initial_state[i, j - 1]
                    initial_state[i,j] = initial_state[i, j - 2] + 2 * hx * (-1 * (Phi_s(surf_temp, amb_temp, natural=natural))/k)

                #central difference with boundaries set to Ta.
                # if i == 0:                  #bottom
                #     initial_state[i + 1, j] = (k * (initial_state[i + 2, j] - amb_temp)/(-2*H_Natural()))
                # if i == initial_y_dim - 1:  #top
                #
                # if j == 0:                  #left
                #
                # if j == initial_x_dim - 1:  #right


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


            elif not natural:
                if i == 0:  # bottom boundary
                    surf_temp = initial_state[i + 1, j]
                    initial_state[i, j] = surf_temp - 2 * hx * H_Forced(wind_speed) * (surf_temp - amb_temp)
                if i == initial_y_dim - 1:  # top boundary
                    surf_temp = initial_state[i - 1, j]
                    initial_state[i, j] = surf_temp - 2 * hx * H_Forced(wind_speed) * (surf_temp - amb_temp)
                if j == 0:  # left boundary
                    surf_temp = initial_state[i, j + 1]
                    initial_state[i, j] = surf_temp - 2 * hx * H_Forced(wind_speed) * (surf_temp - amb_temp)
                if j == initial_x_dim - 1:  # right boundary
                    surf_temp = initial_state[i, j - 1]
                    initial_state[i, j] = surf_temp - 2 * hx * H_Forced(wind_speed) * (surf_temp - amb_temp)

    return initial_state

def Jacobi_Solve(x_range, y_range, x_points = 10, y_points = 10, initial_guess = 0, natural = True):
    #definitions
    hx = x_range / x_points
    hy = y_range / y_points

    initial_x_dim = x_points + 2
    initial_y_dim = y_points + 2
    initial_state = np.full((initial_y_dim, initial_x_dim), initial_guess)

    #initial boundary conditions
    amb_temp = 20
    wind_speed = 30
    k = 150
    q = 0.5e9
    #q = 0

    for iteration in range(3000):
        final_state = np.zeros((initial_y_dim, initial_x_dim))
        initial_state = Neumann_Boundaries(initial_state, hx, hy, amb_temp, wind_speed, k, natural)
        #a = 3 #test
        #solving iteration of Jacobi method
        for i in range(1, initial_y_dim - 1): #y
            for j in range(1, initial_x_dim - 1): #x
                c = 1 / (2 * ((hy ** 2) + (hx ** 2)))
                s = - q / k
                hy2 = np.square(hy)
                hx2 = np.square(hx)
                #updated_value = (((1/(hx**2)) * initial_state[i+1, j]) + ((1/(hx**2)) * initial_state[i-1, j]) + ((1/(hy**2)) * initial_state[i, j-1]) + ((1/(hy**2)) * initial_state[i, j+1]) - s) / ((2/(hx**2)) + (2/(hy**2)))
                #updated_value = c * (((hy**2) * initial_state[i - 1, j]) + ((hy**2) * initial_state[i + 1, j]) + ((hx**2) * initial_state[i, j + 1]) + ((hx**2) * initial_state[i, j - 1]) - ((hx**2) * (hy**2) * s))
                #updated_value = c * (((hx**2) * (initial_state[i-1,j] + initial_state[i+1,j])) + ((hy**2) * (initial_state[i,j-1] + initial_state[i,j+1])) - ((hy**2) * (hx**2) * s))
                updated_value = c * (hy2 * (initial_state[i, j - 1] + initial_state[i, j + 1]) + hx2 * (initial_state[i - 1, j] + initial_state[i + 1, j]) - hx2 * hy2 * s)
                final_state[i,j] = updated_value
                a = 1
        initial_state = final_state
        #pass

    #tidies up array
    final_state = np.delete(final_state, 0, 0)
    final_state = np.delete(final_state, 0, 1)
    final_state = np.delete(final_state, initial_y_dim - 2, 0)
    final_state = np.delete(final_state, initial_x_dim - 2, 1)

    avg_temp = np.average(final_state)
    print()
    print(final_state)
    print(avg_temp)
    return final_state


Jacobi_Solve(0.014, 0.001, x_points= 140, y_points=10, initial_guess=8000)


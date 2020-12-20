import numpy as np
import copy


def h_natural(surf_temp, amb_temp):
    if surf_temp - amb_temp >= 0:
        return np.abs(1.31 * ((float(surf_temp) - amb_temp) ** (1 / 3)))
    else:
        return -1 * np.abs(1.31 * ((float(surf_temp) - amb_temp) ** (1 / 3)))


def h_forced(wind_speed):
    return 11.4 + 5.7 * wind_speed


def phi_s(surf_temp=0, amb_temp=0, wind_speed=0, natural=True):
    if natural:
        return h_natural(surf_temp, amb_temp) * (surf_temp - amb_temp)
    else:
        return h_forced(wind_speed) * (surf_temp - amb_temp)


def ambient_boundaries(initial_state, amb_temp):
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

    return initial_state

#Corner boundary central difference
def bottom_left(initial_T, y, x, hx, hy, amb_T, H, k, q):
    hx2 = np.square(hx)
    hy2 = np.square(hy)

    updated_T = (H * amb_T * (hy2 + hx2) - k * (hy2 * initial_T[y, x+1] + hx2 * initial_T[y+1, x]) - hx * hy * q) \
                / (H * (hy2 + hx2) - k * (hy2 + hx2))

    return updated_T

def bottom_right(initial_T, y, x, hx, hy, amb_T, H, k, q):
    hx2 = np.square(hx)
    hy2 = np.square(hy)

    updated_T = (H * amb_T * (hy2 + hx2) - k * (hy2 * initial_T[y, x - 1] + hx2 * initial_T[y + 1, x]) - hx * hy * q) \
                / (H * (hy2 + hx2) - k * (hy2 + hx2))

    return updated_T

def top_left(initial_T, y, x, hx, hy, amb_T, H, k, q):
    hx2 = np.square(hx)
    hy2 = np.square(hy)

    updated_T = (H * amb_T * (hy2 + hx2) - k * (hy2 * initial_T[y, x+1] + hx2 * initial_T[y-1, x]) - hx * hy * q) \
                / (H * (hy2 + hx2) - k * (hy2 + hx2))

    return updated_T

def top_right(initial_T, y, x, hx, hy, amb_T, H, k, q):
    hx2 = np.square(hx)
    hy2 = np.square(hy)

    updated_T = (H * amb_T * (hy2 + hx2) - k * (hy2 * initial_T[y, x-1] + hx2 * initial_T[y-1, x]) - hx * hy * q) \
                / (H * (hy2 + hx2) - k * (hy2 + hx2))

    return updated_T

#Side boundary central difference
def bottom(initial_T, y, x, hx, hy, amb_T, H, k, q):
    hx2 = np.square(hx)
    hy2 = np.square(hy)

    updated_T = (k * (hy2/2 + initial_T[y, x+1] - hy2/2 * initial_T[y, x-1] - hx2 * initial_T[y+1, x]) + H * hx2 * amb_T - hx * hy * q)\
                / (hx2 * (H - k))

    return updated_T


def top(initial_T, y, x, hx, hy, amb_T, H, k, q):
    hx2 = np.square(hx)
    hy2 = np.square(hy)

    updated_T = (k * (hy2 / 2 + initial_T[y, x - 1] - hy2 / 2 * initial_T[y, x + 1] - hx2 * initial_T[y - 1, x]) + H * hx2 * amb_T - hx * hy * q) \
                / (hx2 * (H - k))

    return updated_T

def left(initial_T, y, x, hx, hy, amb_T, H, k, q):
    hx2 = np.square(hx)
    hy2 = np.square(hy)

    updated_T = (k * (hx2 / 2 + initial_T[y + 1, x] - hx2 / 2 * initial_T[y - 1, x] - hy2 * initial_T[y, x + 1]) + H * hy2 * amb_T - hx * hy * q) \
                / (hy2 * (H - k))

    return updated_T

def right(initial_T, y, x, hx, hy, amb_T, H, k, q):
    hx2 = np.square(hx)
    hy2 = np.square(hy)

    updated_T = (k * (hx2 / 2 + initial_T[y - 1, x] - hx2 / 2 * initial_T[y + 1, x] - hy2 * initial_T[y, x - 1]) + H * hy2 * amb_T - hx * hy * q) \
                / (hy2 * (H - k))

    return updated_T

def interior(initial_T, y, x, hx, hy, k, q):
    hx2 = np.square(hx)
    hy2 = np.square(hy)
    c = 1 / (2 * (hy2 + hx2))
    s = - q / k

    updated_T = c * (hy2 * (initial_T[y, x - 1] + initial_T[y, x + 1]) + hx2 * (initial_T[y - 1, x] + initial_T[y + 1, x]) - hx2 * hy2 * s)

    return updated_T

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
    q = 0.5e9
    #q = 0

    initial_state = ambient_boundaries(initial_state, amb_temp)

    for iteration in range(10000):
        final_state = np.full((initial_y_dim, initial_x_dim), amb_temp)
        # a = 3 #test
        # solving iteration of Jacobi method
        for y in range(1, initial_y_dim - 1):  # y
            for x in range(1, initial_x_dim - 1):  # x

                H = h_natural(initial_state[y,x], amb_temp)


                #Flux CDS
                #corner conditions
                if y == 1 and x == 1: #bottom left corner
                    updated_value = bottom_left(initial_state, y, x, hx, hy, amb_temp, H, k, q)

                elif y == 1 and x == initial_x_dim - 2: #bottom right corner
                    updated_value = bottom_right(initial_state, y, x, hx, hy, amb_temp, H, k, q)

                elif y == initial_y_dim - 2 and x == 1: #top left corner
                    updated_value = top_left(initial_state, y, x, hx, hy, amb_temp, H, k, q)

                elif y == initial_y_dim - 2 and x == initial_x_dim - 2: #top right corner
                    updated_value = top_right(initial_state, y, x, hx, hy, amb_temp, H, k, q)

                #side conditions
                elif y == 1: #bottom side
                    updated_value = bottom(initial_state, y, x, hx, hy, amb_temp, H, k, q)

                elif y == initial_y_dim - 2: #top side
                    updated_value = top(initial_state, y, x, hx, hy, amb_temp, H, k, q)

                elif x == 1: #left side
                    updated_value = left(initial_state, y, x, hx, hy, amb_temp, H, k, q)

                elif x == initial_x_dim - 2: # right side
                    updated_value = right(initial_state, y, x, hx, hy, amb_temp, H, k, q)

                #General CDS
                else:
                    updated_value = interior(initial_state, y, x, hx, hy, k, q)

                final_state[y, x] = updated_value
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


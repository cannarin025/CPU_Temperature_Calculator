import numpy as np
from Functions import *

#Generic element class to be customized e.g. processor or casing
class Element:

    _mounted_top = None
    _mounted_bottom = None

    def __init__(self, x_dim, y_dim, h = 0.1, k = 100, q = 0, amb_temp = 20, initial_guess = 0, natural = True):
        self._x_dim = x_dim
        self._ydim = y_dim
        self._h = h
        self._k = k
        self._q = q
        self._natural = natural
        self._amb_temp = amb_temp
        self._avg_temp = 0
        self._initial_guess = initial_guess
        self._initial_x_dim = int((x_dim / h) + 2)
        self._initial_y_dim = int((y_dim / h) + 2)
        self._initial_state = np.full((self._initial_y_dim, self._initial_x_dim), initial_guess)
        self._k_array = np.full((self._initial_y_dim, self._initial_x_dim), k)
        self._q_array = np.full((self._initial_y_dim, self._initial_x_dim), q)
        self._final_state = np.zeros((self._initial_y_dim, self._initial_x_dim))

    #Getters and Setters
    def get_x_dim(self):
        return self._x_dim

    def get_y_dim(self):
        return self._y_dim

    def get_initial_x_dim(self):
        return self._initial_x_dim

    def get_initial_y_dim(self):
        return self._initial_y_dim

    def get_h(self):
        return self._h

    def get_k(self, x, y):
        return self._k_array[y,x]

    def get_q(self, x, y):
        return self._q_array[y,x]

    def get_initial_temp(self, x, y):
        return self._initial_state[y, x]

    def get_final_temp(self, x, y):
        return self._final_state[y, x]

    def get_initial_temp_array(self):
        return self._initial_state

    def get_final_temp_array(self):
        return self._final_state

    def get_avg_temp(self):
        return np.average(self._final_state)

    def get_mounted_top(self):
        return self._mounted_top

    def get_mounted_bottom(self):
        return self._mounted_bottom

    def set_initial_temp(self, x, y, value):
        self._initial_state[y, x] = value

    def set_final_temp(self, x, y, value):
        self._final_state[y, x] = value

    def set_mounted_top(self, object):
        self._mounted_top = object

    def set_mounted_bottom(self, object):
        self._mounted_bottom = object

    # Methods
    def reset_final_temp(self):
        self._final_state = np.zeros((self._initial_y_dim, self._initial_x_dim))

    def reset_initial_temp(self):
        self._initial_state = np.full((self._initial_y_dim, self._initial_x_dim), self._initial_guess)

    def iteration_end(self):
        self._initial_state = self._final_state

    def finalize_array(self):  # Cleans up array by dropping ghost rows and column
        self._final_state = np.delete(self._final_state, 0, 0)
        self._final_state = np.delete(self._final_state, 0, 1)
        self._final_state = np.delete(self._final_state, self._initial_y_dim - 2, 0)
        self._final_state = np.delete(self._final_state, self._initial_x_dim - 2, 1)

    #Mounting code
    def get_bounds(self, object): #finds ranges of x values of common boundary
        if object.get_h() != self.get_h():
            raise Exception("Grid step sizes for objects being joined must be identical!")

        if object.get_x_dim() % 2 != 0 or self.get_x_dim() % 2 != 0:
            raise Exception("Objects must be even length for mounting to work!")

        h = self.get_h()

        if object.get_x_dim() > self.get_x_dim():
            lx = object.get_x_dim()
            sx = self.get_x_dim()
            # lx = object.get_initial_x_dim() - 2
            # sx = self.get_initial_x_dim() - 2

            boundary_start = (lx / 2) - (sx / 2) + 1  # accounts for horizontal ghost points
            boundary_end = (lx / 2) + (sx / 2) + 1  # accounts for horizontal ghost points

        else:
            lx = self.get_x_dim()
            sx = object.get_x_dim()
            # lx = object.get_initial_x_dim() - 2
            # sx = self.get_initial_x_dim() - 2
            boundary_start = (((lx / 2) - (sx / 2))/h) + 1  # accounts for horizontal ghost points
            boundary_end = (((lx / 2) + (sx / 2))/h) + 1  # accounts for horizontal ghost points

        return int(boundary_start), int(boundary_end)

    def __mount(self, object, mount_y): #Creates boundary
        boundary_start, boundary_end = self.get_bounds(object)
        for x in range(boundary_start, boundary_end):
            self.set_initial_temp(x,mount_y, -50)

    def mount_top(self, object, first_call = None): #mounts object above self
        if first_call is False:
            return

        if first_call is None:
            first_call = False

        if not isinstance(object, Element):
            print("Object cannot be mounted. Is not an Element")
            return

        if self.get_mounted_top() is not None:
            print("This object is already mounted ontop")
            return

        if object.get_mounted_bottom() is not None and not first_call:
            print("Target object is already mounted on bottom")
            return

        mount_y = self._initial_y_dim - 2
        self.__mount(object, mount_y)
        self.set_mounted_top(object)
        object.mount_bottom(self, not first_call)

    def mount_bottom(self, object, first_call = None): #mounts object below self
        if first_call is False:
            return

        if first_call is None:
            first_call = False

        if not isinstance(object, Element):
            print("Object cannot be mounted. Is not an Element")
            return

        if self.get_mounted_bottom() is not None:
            print("This object is already mounted underneath")
            return

        if object.get_mounted_top() is not None and not first_call:
            print("Target object is already mounted on top")
            return

        mount_y = 1
        self.__mount(object, mount_y)
        self.set_mounted_bottom(object)

        object.mount_top(self, not first_call)


    # def unmount_object(self, side):
    #     if side == "top":
    #         self.set_mounted_top()
    #         object.set
    #     elif side == "bottom"
    #
    #     else:
    #         print("No valid side entered")
    #         return


    def Apply_Neumann_Boundaries(self, joined = False, other = None):
        if joined:
            pass
        else:
            for y in range(self._initial_y_dim):
                for x in range(self._initial_x_dim):
                    if self._natural:

                        """Central Difference"""
                        # central difference calculated by hand (does not work as the one above does)
                        if y == 0:  # bottom
                            surf_temp = self.get_initial_temp(x, y + 1)
                            phi_s = Phi_s(surf_temp, self._amb_temp, natural=self._natural)
                            ghost_T = self.get_initial_temp(x, y + 2) + 2 * self._h * (-1 * phi_s / self.get_k(x, y))
                            self.set_initial_temp(x, y, ghost_T)

                        if y == self._initial_y_dim - 1:  # top
                            surf_temp = self.get_initial_temp(x, y - 1)
                            phi_s = Phi_s(surf_temp, self._amb_temp, natural=self._natural)
                            ghost_T = self.get_initial_temp(x, y - 2) + 2 * self._h * (-1 * phi_s / self.get_k(x, y))
                            self.set_initial_temp(x, y, ghost_T)

                        if x == 0:  # left
                            surf_temp = self.get_initial_temp(x + 1, y)
                            phi_s = Phi_s(surf_temp, self._amb_temp, natural=self._natural)
                            ghost_T = self.get_initial_temp(x + 2, y) + 2 * self._h * (-1 * phi_s / self.get_k(x, y))
                            self.set_initial_temp(x, y, ghost_T)

                        if x == self._initial_x_dim - 1:  # right
                            surf_temp = self.get_initial_temp(x - 1, y)
                            phi_s = Phi_s(surf_temp, self._amb_temp, natural=self._natural)
                            ghost_T = self.get_initial_temp(x - 2, y) + 2 * self._h * (-1 * phi_s / self.get_k(x, y))
                            self.set_initial_temp(x, y, ghost_T)

    def Jacobi_Iteration(self):
        self.reset_final_temp()
        self.Apply_Neumann_Boundaries(joined=False, other=None) #no joined elements
        # solving iteration of Jacobi method
        for y in range(1, self._initial_y_dim - 1):  # y
            for x in range(1, self._initial_x_dim - 1):  # x
                q = self.get_q(x,y)
                k = self.get_k(x,y)
                h2 = np.square(self._h)
                new_T = 0.25 * (self.get_initial_temp(x - 1, y)
                                + self.get_initial_temp(x + 1, y)
                                + self.get_initial_temp(x, y - 1)
                                + self.get_initial_temp(x, y + 1)
                                + h2 * q / k)

                self.set_final_temp(x, y, new_T)

    def Jacobi_Solve(self, max_iterations):
        for iteration in range(max_iterations):
            self.Jacobi_Iteration() #solves for current  iteration
            self.iteration_end()  #resets initial array to final array to prepare for next iteration

        self.finalize_array()
        self._avg_temp = self.get_avg_temp()
        print(self._final_state)
        print(self._avg_temp)
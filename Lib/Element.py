import numpy as np
from Lib.Functions import *
from Lib.BoundaryRef import BoundaryRef
import seaborn as sb
import matplotlib.pyplot as plt
import numpy as np

#Generic element class to be customized e.g. processor or casing
class Element:

    _mounted_top = None
    _mounted_bottom = None
    _power_out = 0
    _final = False

    def __init__(self, name, x_dim, y_dim, h = 0.1, k = 100, q = 0, amb_temp = 20, initial_guess = 0, tolerance = False, natural = True):
        self._name = name
        self._x_dim = x_dim
        self._y_dim = y_dim
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
        self._power_produced = q * (self._initial_x_dim - 2) * (self._initial_y_dim - 2)
        self._convergence_tolerance = tolerance

    #Getters and Setters
    def get_name(self):
        return self._name

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
        if self._final:
            return np.average(self._final_state)
        else:
            print("Please finalize array before finding average!")

    def get_power_out(self):
        return self._power_out

    def get_power_produced(self):
        return self._power_produced

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
        if not self._final:
            self._final_state = np.delete(self._final_state, 0, 0)
            self._final_state = np.delete(self._final_state, 0, 1)
            self._final_state = np.delete(self._final_state, self._initial_y_dim - 2, 0)
            self._final_state = np.delete(self._final_state, self._initial_x_dim - 2, 1)
            self._final = True

        else:
            print("Array has already been tidied!")

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

            boundary_start = (((lx / 2) - (sx / 2)) / h) + 1  # accounts for horizontal ghost points
            boundary_end = (((lx / 2) + (sx / 2)) / h) + 1  # accounts for horizontal ghost points

        else:
            lx = self.get_x_dim()
            sx = object.get_x_dim()
            # lx = object.get_initial_x_dim() - 2
            # sx = self.get_initial_x_dim() - 2
            boundary_start = (((lx / 2) - (sx / 2))/h) + 1  # accounts for horizontal ghost points
            boundary_end = (((lx / 2) + (sx / 2))/h) + 1  # accounts for horizontal ghost points
            # boundary_start = 1
            # boundary_end = self.get_initial_x_dim() - 1

        return int(boundary_start), int(boundary_end)

    def __mount(self, object, mount_y, boundary_ref): #Creates boundary
        boundary_start, boundary_end = self.get_bounds(object)

        if self.get_initial_x_dim() > object.get_initial_x_dim():
            boundary_ref.set_self_boundary_start(boundary_start)
            boundary_ref.set_self_boundary_end(boundary_end)

        else:
            boundary_ref.set_self_boundary_start(1)
            boundary_ref.set_self_boundary_end(self.get_initial_x_dim() - 1)

        if boundary_end - boundary_start == self._initial_x_dim - 2: #case self is shorter. (sets entire side as boundary)
            for x in range(1, self._initial_x_dim - 1):
                #self.set_final_temp(x, mount_y, -50) #todo: REMOVE
                pass

        else:
            for x in range(boundary_start, boundary_end): #case where self is longer. (sets required length)
                #self.set_final_temp(x,mount_y, -50) #todo: REMOVE
                pass

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
        offset = (self._initial_x_dim - object.get_initial_x_dim())/2
        self.set_mounted_top(BoundaryRef(object=object,x_offset=offset, self_mount_y=mount_y, object_mount_y=1))
        self.__mount(object, mount_y, self.get_mounted_top())
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
        offset = (self._initial_x_dim - object.get_initial_x_dim()) / 2
        self.set_mounted_bottom(BoundaryRef(object=object, x_offset=offset, self_mount_y=mount_y, object_mount_y=object._initial_y_dim - 2))
        self.__mount(object, mount_y, self.get_mounted_bottom())

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

    def __apply_neumann_boundaries(self):
        for y in range(self._initial_y_dim):
            for x in range(self._initial_x_dim):
                if self._natural:

                    """Central Difference"""
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

    def __update_CDS(self, x, y):
        q = self.get_q(x,y)
        k = self.get_k(x,y)
        h2 = np.square(self._h)
        new_T = 0.25 * (self.get_initial_temp(x - 1, y)
                        + self.get_initial_temp(x + 1, y)
                        + self.get_initial_temp(x, y - 1)
                        + self.get_initial_temp(x, y + 1)
                        + h2 * q / k)

        return new_T

    def __mounted_CDS_bottom(self, x, y):
        boundary_ref = self.get_mounted_bottom()
        other = boundary_ref.get_object()
        ref_x = boundary_ref.convert_coordinate(x)
        ref_y = boundary_ref.get_object_mount_y()
        if x in range(boundary_ref.get_self_boundary_start(), boundary_ref.get_self_boundary_end()):
            h2 = np.square(self._h)
            q = self.get_q(x, y)
            k = self.get_k(x, y)
            bottom_k = 2 / (1 / k + 1 / other.get_k(ref_x, ref_y))
            k_sum = 3 * k + bottom_k
            s = q * h2

            new_T = (bottom_k * other.get_initial_temp(ref_x, ref_y)
                     + k * self.get_initial_temp(x, y + 1)
                     + k * self.get_initial_temp(x - 1, y)
                     + k * self.get_initial_temp(x + 1, y) + s) / k_sum

        else:
            new_T = self.__update_CDS(x, y)

        return new_T

    def __mounted_CDS_top(self, x, y):

        boundary_ref = self.get_mounted_top()
        other = boundary_ref.get_object()
        ref_x = boundary_ref.convert_coordinate(x)
        ref_y = boundary_ref.get_object_mount_y()
        if x in range(boundary_ref.get_self_boundary_start(), boundary_ref.get_self_boundary_end()):
            h2 = np.square(self._h)
            q = self.get_q(x, y)
            k = self.get_k(x, y)
            top_k = 2 / (1 / k + 1 / other.get_k(ref_x, ref_y))
            k_sum = 3 * k + top_k
            s = q * h2

            new_T = (top_k * other.get_initial_temp(ref_x, ref_y)
                     + k * self.get_initial_temp(x, y - 1)
                     + k * self.get_initial_temp(x - 1, y)
                     + k * self.get_initial_temp(x + 1, y) + s) / k_sum

        else:
            new_T = self.__update_CDS(x, y)

        return new_T

    def jacobi_iteration(self):
        self._flux_out = 0 #resets flux for next iteration
        self.reset_final_temp()
        self.__apply_neumann_boundaries()
        # solving iteration of Jacobi method
        for y in range(1, self._initial_y_dim - 1):  # y
            for x in range(1, self._initial_x_dim - 1):  # x
                #mounted CDS
                if y == 1 and self.get_mounted_bottom() is not None: #on bottom boundary and mounted
                    new_T = self.__mounted_CDS_bottom(x,y)

                elif y == self._initial_y_dim - 2 and self.get_mounted_top() is not None:  # on top boundary and mounted
                    new_T = self.__mounted_CDS_top(x,y)

                else: #Ignoring mounting effects
                    new_T = self.__update_CDS(x,y)

                    if y == 1 or x == 1 or y == self._initial_y_dim - 2 or x == self._initial_x_dim - 2:
                        self._flux_out += self._h * Phi_s(self.get_initial_temp(x,y), self._amb_temp, natural=self._natural) #sums flux over all exposed sides

                self.set_final_temp(x, y, new_T)

    def jacobi_solve(self, max_iterations): #Only solves for this element in system. Does not handle interaction.
        iteration = 0
        while iteration < max_iterations or np.abs(self._power_out - self._power_produced) <= self._convergence_tolerance:
            self.jacobi_iteration() #solves for current  iteration
            self.iteration_end()  #resets initial array to final array to prepare for next iteration

        self.finalize_array()
        self._avg_temp = self.get_avg_temp()

    def save_data(self):
        if self._final:
            file_name = f"{self._name}_data"
            file_path = f"Data\\{file_name}.csv"
            np.savetxt(file_path, self._final_state, delimiter=",")

    def graph_temperature(self):
        if self._final:

            x = np.arange(0, self._x_dim, self._h)
            y = np.arange(0, self._y_dim, self._h)

            fig, ax1 = plt.subplots()
            fig.subplots_adjust(bottom=0.2)
            sb.set(font_scale=1.7)
            ax2 = sb.heatmap(self._final_state, cmap="coolwarm", xticklabels=x, yticklabels=y, ax=ax1)
            #np.flipud(self._final_state) flipped array
            if self._name is not None:
                ax2.set_title(f"{self._name} Temp Variation")
            plt.xlabel("x [mm]")
            plt.ylabel("y [mm]")
            sb.set(font_scale=1)
            ax1.tick_params(labelsize=10)
            ax2.figure.axes[-1].set_ylabel("Temperature (°C)", size=16)
            plt.show()
        else:
            print("Please finalise data before plotting!")

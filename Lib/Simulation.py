from Lib.Element import Element
from Lib.HeatSink import HeatSink
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sb


class Simulation:
    _object_list = []

    def __init__(self, ambient_temp=20, wind_speed=20, grid_spacing=0.1, initial_guess=0, tolerance=False,
                 natural=True):
        self._ambient_temp = ambient_temp
        self._wind_speed = wind_speed
        self._grid_spacing = grid_spacing
        self._initial_guess = initial_guess
        self._tolerance = tolerance
        self._natural = natural

    # utility
    def check_unique_name(self, new_name):
        names = []

        if self._object_list == []:
            return True

        for object in self._object_list:
            name = object.get_name()
            if name not in names:
                names.append(name)

        if new_name not in names:
            return True

        else:
            return False

    def get_object_by_name(self, name):
        for object in self._object_list:
            if object.get_name() == name:
                return object

    # setup
    def add_processor(self, name, x_dim, y_dim, q=0.5, k=150e-3):
        if self.check_unique_name(name):
            processor = Element(x_dim=x_dim, y_dim=y_dim, h=self._grid_spacing, k=k, q=q, amb_temp=self._ambient_temp,
                                initial_guess=self._initial_guess, tolerance=self._tolerance, natural=self._natural,
                                name=name)
            self._object_list.append(processor)
        else:
            raise Exception(f'The name "{name}" is not unique')

    def add_ceramic(self, name, x_dim, y_dim, k=230e-3):
        if self.check_unique_name(name):
            ceramic = Element(x_dim=x_dim, y_dim=y_dim, h=self._grid_spacing, k=k, q=0, amb_temp=self._ambient_temp,
                              initial_guess=self._initial_guess, tolerance=self._tolerance, natural=self._natural,
                              name=name)
            self._object_list.append(ceramic)
        else:
            raise Exception(f'The name "{name}" is not unique')

    def add_heat_sink(self, name="HS", n_fins=8, fin_height=5, fin_width=2, fin_spacing=2, k=250e-3):
        if self.check_unique_name(name):
            heat_sink = HeatSink(h=self._grid_spacing, k=k, q=0, amb_temp=self._ambient_temp,
                                 initial_guess=self._initial_guess, tolerance=False, natural=True, name=name,
                                 n_fins=n_fins, fin_height=fin_height, fin_width=fin_width, fin_spacing=fin_spacing)
            self._object_list.append(heat_sink)
        else:
            raise Exception(f'The name "{name}" is not unique')

    def order_object_list(
            self):  # todo: need to write function to sort object list to ensure elements are solved in correct order i.e. bottom to top.
        pass

    def mount_to_bottom(self, target_name, source_name):  # mounts source under target
        target = self.get_object_by_name(target_name)
        source = self.get_object_by_name(source_name)
        target.mount_bottom(source)

    def mount_to_top(self, target_name, source_name):  # mounts source ontop of target
        target = self.get_object_by_name(target_name)
        source = self.get_object_by_name(source_name)
        target.mount_top(source)

    # solving
    def jacobi_solve(self, max_iterations):
        convergence = False
        iteration = 0
        while iteration < max_iterations and convergence is False:

            if iteration % 100 == 0:
                print("Current iteration:", iteration)

            for element in self._object_list:  # runs iterations
                element.jacobi_iteration()

            for element in self._object_list:  # ends iterations
                element.iteration_end()

            iteration += 1

        if convergence:
            print("Done! Convergence achieved")

        elif iteration == max_iterations:
            print("Done! Max iterations reached")

        for element in self._object_list:
            element.finalize_array()
            print(f"Avg temp of {element.get_name()} is: ", element.get_avg_temp())

    # output
    def save_data(self):
        for element in self._object_list:
            element.save_data()

    def graph_individual(self):
        for element in self._object_list:
            element.graph_temperature()

    # method for graphing entire system
    def graph_system(self):
        elements_from_bottom = []  # a list of objects in the system from bottom to top
        system_height = 0
        system_width = 0
        for element in self._object_list:
            system_height += element.get_y_dim()
            if element.get_x_dim() > system_width:
                system_width = element.get_x_dim()

            if element.get_mounted_bottom() is None:
                elements_from_bottom.append(element)

        system_array = np.full((int(system_height / self._grid_spacing), int(system_width / self._grid_spacing)), self._initial_guess)  # adjust value array is filled with to set "external temps" values todo: find good value for this to be

        for i in range(len(self._object_list) - 1):  # loops over remaining elements in system and builds ordered list.
            elements_from_bottom.append(elements_from_bottom[-1].get_mounted_top().get_object())

        # merges all object arrays such that they can be displayed as one. todo: can this be made more efficient?
        y_start = 0
        for element in elements_from_bottom:
            element_array = element.get_final_temp_array()
            diff = (system_array.shape[1] - element_array.shape[1]) / 2
            for j in range(element_array.shape[0]):  # y dim of array
                a = element_array.shape[0]
                count = 0
                for i in range(system_array.shape[1]):  # x dim of array
                    if diff <= i < system_array.shape[1] - diff:
                        system_array[int(y_start) + j, i] = element_array[j, count]
                        count += 1

            y_start += (element.get_y_dim() / self._grid_spacing)

        fig, ax1 = plt.subplots()
        fig.subplots_adjust(bottom=0.2)
        sb.set(font_scale=1.7)
        ax2 = sb.heatmap(system_array, cmap="coolwarm", xticklabels="x", yticklabels="y", ax=ax1)
        # np.flipud(self._final_state) flipped array
        plt.xlabel("x [mm]")
        plt.ylabel("y [mm]")
        sb.set(font_scale=1)
        ax1.tick_params(labelsize=10)
        ax2.figure.axes[-1].set_ylabel("Temperature (°C)", size=16)
        plt.show()

# count = 0
# for i in range(len(c)):
#     if i >= diff and i < len(a) - diff:
#         c[i] = b[count]
#         count += 1
#
# print(c)

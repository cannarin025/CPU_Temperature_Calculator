from Lib.Element import Element
from Lib.Functions import *
from Lib.SurfaceCell import SurfaceCell
import math

class HeatSink(Element):

    _x_dim = 0
    _y_dim = 0
    _initial_x_dim = 0
    _initial_y_dim = 0
    __surface_cells = []

    def __init__(self, name, n_fins, fin_height, fin_width, fin_spacing, base_thickness = 4, h = 0.1, k = 250e-3, q = 0, amb_temp = 20, initial_guess = 0, tolerance = False, natural = True): #input values in mm
        """
        :param name:            dtype:string            name of component
        :param n_fins:          dtype: int              no of fins
        :param fin_height:      dtype: float            height of fins in mm above 4mm base
        :param fin_width:       dtype: float            width of fins in mm
        :param fin_spacing:     dtype: float            spacing of fins in mm
        :param h:               dtype: float            spacing of grid cells in mm
        :param k:               dtype: float            conductivity of material
        :param q:               dtype: float            power generated per mm^3 inside element
        :param amb_temp:        dtype: float            ambient temperature in Celcius
        :param initial_guess:   dtype: float            initial guess for final temperature of element
        :param tolerance:       dtype: float            tolerance for convergence
        :param natural:         dtype: bool             if natural or forced convection is used
        """
        # super().__init__(self, name, x_dim, y_dim, h, k, q, amb_temp, initial_guess, tolerance, natural)
        self._name = name
        self._n_fins = n_fins
        self._fin_height = fin_height
        self._fin_width = fin_width
        self._fin_spacing = fin_spacing
        self._base_thickness = base_thickness
        self._h = h
        self._k = k
        self._q = q
        self._amb_temp = amb_temp
        self._initial_guess = initial_guess
        self._tolerance = tolerance
        self._natural = natural

        if self._fin_spacing < 2*self._h:
            raise Exception("Fin spacing must be atleast two cell lengths!")

        if is_divisible(self._fin_spacing, self._h) and is_divisible(self._fin_width, self._h) and is_divisible(self._fin_height + self._base_thickness, self._h) and is_divisible(self._base_thickness, self._h):
            self._x_dim = (self._fin_width + self._fin_spacing) * (self._n_fins - 1) + self._fin_width  # width of heatsink in mm

            if self._x_dim % 2 != 0:  # checks head sink width is even to make centering on ceramic easier.
                raise Exception("Heat sink width must be even. Current width:", self._x_dim, "mm")

            self._y_dim = self._base_thickness + self._fin_height  # height of heatsink in mm
            self._initial_x_dim = int(self._x_dim / self._h) + 2
            self._initial_y_dim = int((self._fin_height / self._h) + (self._base_thickness / self._h)) + 2
            self._k_array = np.full((self._initial_y_dim, self._initial_x_dim), self._k, dtype=float)
            self._q_array = np.full((self._initial_y_dim, self._initial_x_dim), self._q, dtype=float)
            self._fin_cells = self._fin_width / self._h
            self._space_cells = self._fin_spacing / self._h
            fin = True

            #self._initial_state = np.zeros((self._initial_y_dim, self._initial_x_dim))
            self._initial_state = np.full((self._initial_y_dim, self._initial_x_dim), self._initial_guess, dtype=float)
            self._final_state = np.full((self._initial_y_dim, self._initial_x_dim), self._initial_guess, dtype=float)  # todo: how should fin final temp be initialised to not cause issues with GS method?

            for y in range(1, self._initial_y_dim - 1):  # looping over "real" cells
                fin = True
                cell_count = 0
                for x in range(1, self._initial_x_dim - 1):  # looping over "real" cells
                    if y <= self._base_thickness / self._h:
                        self.set_initial_temp(x, y, self._initial_guess)
                        self.set_final_temp(x, y, self._initial_guess)  # initialises final temp array to contain 0

                        if y >= 1:
                            if (x == 1 or x == self._initial_x_dim - 2) and y == 1:
                                self.__surface_cells.append(SurfaceCell((x, y), 2))  # cell is on corner
                            elif (x == 1 or x == self._initial_x_dim - 2):
                                self.__surface_cells.append(SurfaceCell((x, y), 1))  # cell is on edge

                    elif y > self._base_thickness / self._h:
                        if fin:  # starts counting on a fin
                            self.set_initial_temp(x, y, self._initial_guess)
                            self.set_final_temp(x, y, self._initial_guess)
                            self.set_k(x, y, self._k)

                            if cell_count == 0:
                                if y == self._initial_y_dim - 2:
                                    self.__surface_cells.append(SurfaceCell((x, y), 2))
                                else:
                                    self.__surface_cells.append(SurfaceCell((x, y), 1))

                            cell_count += 1

                            if cell_count == self._fin_cells:
                                if y == self._initial_y_dim - 2:
                                    self.__surface_cells.append(SurfaceCell((x, y), 2))
                                else:
                                    self.__surface_cells.append(SurfaceCell((x, y), 1))

                                cell_count = 0
                                fin = False  # end of fin

                        else:
                            #self.set_initial_temp(x, y, 0)
                            # leaves space between fins in final array as nan
                            self.set_initial_temp(x, y, self._initial_guess)  # todo: what temp should space between fins be initialised to?
                            cell_count += 1

                            if cell_count == self._space_cells:
                                cell_count = 0
                                fin = True

        else:
            raise Exception("Input heat sink dimensions not evenly divisible into grid")

    def get_temp_array(self):
        """drops ghost points and fills space between fins with nan to be displayed"""
        temp_array = self._final_state.copy()
        for y in range(1, self._initial_y_dim - 1):  # looping over "real" cells
            fin = True
            cell_count = 0
            for x in range(1, self._initial_x_dim - 1):  # looping over "real" cells
                if y > self._base_thickness / self._h:  # once heat sink base ends
                    if fin:  # starts counting on a fin
                        cell_count += 1
                        if cell_count == self._fin_cells:  # last cell of fin
                            cell_count = 0
                            fin = False  # end of fin
                    else:  # space between fins
                        temp_array[y, x] = np.nan  # sets space between fins to nan to be displayed
                        cell_count += 1
                        if cell_count == self._space_cells:  # next fin begins
                            cell_count = 0
                            fin = True

        temp_array = np.delete(temp_array, 0, 0)
        temp_array = np.delete(temp_array, 0, 1)
        temp_array = np.delete(temp_array, self._initial_y_dim - 2, 0)
        temp_array = np.delete(temp_array, self._initial_x_dim - 2, 1)
        return temp_array

    def get_avg_temp(self):
        temp_array = self.get_temp_array()
        cell_count = 0
        temp_total = 0
        y_dim, x_dim = np.shape(temp_array)
        for y in range(y_dim):
            for x in range(x_dim):
                if not math.isnan(temp_array[y, x]):
                    temp_total += temp_array[y, x]
                    cell_count += 1

        avg_temp = temp_total / cell_count
        return avg_temp

    def mount_top(self, target, first_call = None):
        raise Exception("You cannot mount objects ontop of a heat sink. Please mount underneath instead!")

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

        for y in range(int(self._base_thickness / self._h) + 1, int(self._initial_y_dim)):
            fin = True
            cell_count = 0
            for x in range(1, self._initial_x_dim - 1):
                if fin:  # starts counting on a fin

                    cell_count += 1

                    if cell_count == self._fin_cells:
                        x += 1
                        surf_temp = self.get_initial_temp(x - 1, y)
                        phi_s = Phi_s(surf_temp, self._amb_temp, natural=self._natural)
                        ghost_T = self.get_initial_temp(x - 2, y) + 2 * self._h * (-1 * phi_s / self.get_k(x, y))
                        self.set_initial_temp(x, y, ghost_T)

                        cell_count = 0
                        fin = False  # end of fin

                else:
                    cell_count += 1
                    if cell_count < self._space_cells and y == (self._base_thickness / self._h) + 1:
                        surf_temp = self.get_initial_temp(x, y - 1)
                        phi_s = Phi_s(surf_temp, self._amb_temp, natural=self._natural)
                        ghost_T = self.get_initial_temp(x, y - 2) + 2 * self._h * (-1 * phi_s / self.get_k(x, y))
                        self.set_initial_temp(x, y, ghost_T)

                    if cell_count == self._space_cells:
                        surf_temp = self.get_initial_temp(x + 1, y)
                        phi_s = Phi_s(surf_temp, self._amb_temp, natural=self._natural)
                        ghost_T = self.get_initial_temp(x + 2, y) + 2 * self._h * (-1 * phi_s / self.get_k(x, y))
                        self.set_initial_temp(x, y, ghost_T)

                        cell_count = 0
                        fin = True

    def jacobi_iteration(self):
        self._flux_out = 0
        self.reset_final_temp()
        self.__apply_neumann_boundaries()
        a = 1 #todo: delete this. For testing only

        for y in range(1, self._initial_y_dim - 1):
            fin = True
            cell_count = 0
            for x in range(1, self._initial_x_dim - 1):
                new_T = self._amb_temp #so space inbetween fins is ambient temp
                #new_T = np.nan  # sets space between fins to nan         todo: find a better way of doing this.
                #new_T = self.get_initial_temp(x,y)
                if y <= self._base_thickness / self._h:
                    if y == 1 and self.get_mounted_bottom() is not None:
                        new_T = self._Element__mounted_CDS_bottom(x,y)

                    else:
                        new_T = self._Element__update_CDS(x,y)

                elif y > self._base_thickness / self._h:
                    if fin:  # starts counting on a fin
                        new_T = self._Element__update_CDS(x,y)
                        cell_count += 1

                        if cell_count == self._fin_cells:
                            cell_count = 0
                            fin = False  # end of fin

                    else:
                        cell_count += 1

                        if cell_count == self._space_cells:
                            cell_count = 0
                            fin = True

                self.set_final_temp(x,y, new_T)

    def gs_iteration(self):
        self._flux_out = 0
        self.__apply_neumann_boundaries()
        a = 1 #todo: delete this. For testing only

        for y in range(1, self._initial_y_dim - 1):
            fin = True
            cell_count = 0
            for x in range(1, self._initial_x_dim - 1):
                new_T = self._amb_temp #so space inbetween fins is ambient temp
                #new_T = np.nan  # todo: why is space between fins set to nan here?
                #new_T = self.get_initial_temp(x,y)
                if y <= self._base_thickness / self._h:
                    if y == 1 and self.get_mounted_bottom() is not None:
                        new_T = self._Element__gs_mounted_CDS_bottom(x,y)

                    else:
                        new_T = self._Element__gs_update_CDS(x,y)

                elif y > self._base_thickness / self._h:
                    if fin:  # starts counting on a fin
                        new_T = self._Element__gs_update_CDS(x,y)
                        cell_count += 1

                        if cell_count == self._fin_cells:
                            cell_count = 0
                            fin = False  # end of fin

                    else:
                        cell_count += 1

                        if cell_count == self._space_cells:
                            cell_count = 0
                            fin = True

                self.set_final_temp(x,y, new_T)
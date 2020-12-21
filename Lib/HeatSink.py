from Lib.Element import Element
from Lib.Functions import *

class HeatSink(Element):

    _x_dim = 0
    _y_dim = 0

    def __init__(self, name, n_fins, fin_height, fin_width, fin_spacing, h = 0.1, k = 100, q = 0, amb_temp = 20, initial_guess = 0, tolerance = False, natural = True): #input values in mm
        #super().__init__(self, name, x_dim, y_dim, h, k, q, amb_temp, initial_guess, tolerance, natural)
        self._name = name
        self._n_fins = n_fins
        self._fin_height = fin_height
        self._fin_width = fin_width
        self._fin_spacing = fin_spacing
        self._h = h
        self._k = k
        self._k_array = np.empty((1,1))
        self._q = q
        self._amb_temp = amb_temp
        self._initial_guess = initial_guess
        self._tolerance = tolerance
        self._natural = natural

        if self._fin_spacing < 2*self._h:
            raise Exception("Fin spacing must be atleast two cell lengths!")

        if is_divisible(self._fin_spacing, self._h) and is_divisible(self._fin_width, self._h) and is_divisible(self._fin_height + 4, self._h) and is_divisible(4, self._h):
            l = (self._fin_width + self._fin_spacing) * (self._n_fins - 1) + self._fin_width

            if l % 2 != 0:  # checks head sink width is even to make centering on ceramic easier.
                raise Exception("Heat sink width must be even. Current width:", l, "mm")


            # if l < 20:  # checks heat sink is wider than ceramic casing.
            #     print("Heat sink must be atleast as wide as casing. Current width:", l, "mm")
            #     return

            self._x_dim = int(l / self._h) + 1
            self._y_dim = int(self._fin_height / self._h + 4 / self._h)
            self._k_array = np.full((self._y_dim, self._x_dim), self._k)
            self._fin_cells = self._fin_width / self._h
            self._space_cells = self._fin_spacing / self._h
            fin = True

            self._initial_state = np.zeros((self._y_dim + 1, self._x_dim + 1))

            for y in range(1, self._y_dim):
                fin = True
                cell_count = 0
                for x in range(1, self._x_dim):
                    if y < 4 / h:
                        self.set_initial_temp(x, y, self._initial_guess)

                    elif y >= 4 / h:
                        if fin:  # starts counting on a fin
                            self.set_initial_temp(x, y, self._initial_guess)
                            cell_count += 1

                            if cell_count == self._fin_cells:
                                cell_count = 0
                                fin = False  # end of fin

                        else:
                            self.set_initial_temp(x, y, 0)
                            cell_count += 1

                            if cell_count == self._space_cells:
                                cell_count = 0
                                fin = True

        else:
            raise Exception("Input heat sink dimensions not evenly divisible into grid")

    def apply_neumann_boundaries(self):
        for y in range(1, self._y_dim):
            fin = True
            cell_count = 0
            for x in range(1, self._x_dim):
                if y == 0: #bottom
                    surf_temp = self.get_initial_temp(x, y + 1)
                    phi_s = Phi_s(surf_temp, self._amb_temp, natural=self._natural)
                    ghost_T = self.get_initial_temp(x, y + 2) + 2 * self._h * (-1 * phi_s / self.get_k(x, y))
                    self.set_initial_temp(x, y, ghost_T)

                if x == 0: #left
                    surf_temp = self.get_initial_temp(x + 1, y)
                    phi_s = Phi_s(surf_temp, self._amb_temp, natural=self._natural)
                    ghost_T = self.get_initial_temp(x + 2, y) + 2 * self._h * (-1 * phi_s / self.get_k(x, y))
                    self.set_initial_temp(x, y, ghost_T)

                if x == self._x_dim: #right
                    surf_temp = self.get_initial_temp(x - 1, y)
                    phi_s = Phi_s(surf_temp, self._amb_temp, natural=self._natural)
                    ghost_T = self.get_initial_temp(x - 2, y) + 2 * self._h * (-1 * phi_s / self.get_k(x, y))
                    self.set_initial_temp(x, y, ghost_T)

                elif y >= 4 / self._h:
                    if fin:  # starts counting on a fin
                        if y == self._y_dim:
                            #top
                            surf_temp = self.get_initial_temp(x, y - 1)
                            phi_s = Phi_s(surf_temp, self._amb_temp, natural=self._natural)
                            ghost_T = self.get_initial_temp(x, y - 2) + 2 * self._h * (-1 * phi_s / self.get_k(x, y))
                            self.set_initial_temp(x, y, ghost_T)

                        cell_count += 1

                        if cell_count == self._fin_cells:
                            cell_count = 0
                            fin = False  # end of fin
                            #right
                            surf_temp = self.get_initial_temp(x - 1, y)
                            phi_s = Phi_s(surf_temp, self._amb_temp, natural=self._natural)
                            ghost_T = self.get_initial_temp(x - 2, y) + 2 * self._h * (-1 * phi_s / self.get_k(x, y))
                            self.set_initial_temp(x, y, ghost_T)

                    else:
                        cell_count += 1

                        if cell_count == self._space_cells:
                            cell_count = 0
                            fin = True
                            #left
                            surf_temp = self.get_initial_temp(x + 1, y)
                            phi_s = Phi_s(surf_temp, self._amb_temp, natural=self._natural)
                            ghost_T = self.get_initial_temp(x + 2, y) + 2 * self._h * (-1 * phi_s / self.get_k(x, y))
                            self.set_initial_temp(x, y, ghost_T)
import numpy as np
from decimal import Decimal

def is_divisible(num, divisor):
    a = Decimal(str(num))
    b = Decimal(str(divisor))
    c = a % b
    return c.is_zero()

def create_HS(n_fins, h, fin_height, fin_width, fin_spacing): #input values in mm
    heat_sink = None
    if is_divisible(fin_spacing, h) and is_divisible(fin_width, h) and is_divisible(fin_height + 4, h) and is_divisible(4, h):
        l = (fin_width + fin_spacing) * (n_fins - 1) + fin_width

        if l % 2 != 0: #checks head sink width is even to make centering on ceramic easier.
            print("Heat sink width must be even. Current width:", l, "mm")
            return

        if l < 20: #checks heat sink is wider than ceramic casing.
            print("Heat sink must be atleast as wide as casing. Current width:", l, "mm")
            return

        x_dim = int(l / h)
        y_dim = int(fin_height + 4 / h)
        fin_cells = fin_width / h
        space_cells = fin_spacing / h
        fin = True

        heat_sink = np.zeros((y_dim, x_dim))

        for y in range(y_dim):
            fin = True
            cell_count = 0
            for x in range(x_dim):
                if y < 4 / h:
                    heat_sink[y, x] = 1

                if y == 0:
                    if x >= l/2 - 10 and x < l/2 + 10: #centres ceramic casing on heat sink
                        heat_sink[y,x] = 2

                elif y >= 4/h:
                    if fin: #starts counting on a fin
                        heat_sink[y,x] = 1
                        cell_count += 1

                        if cell_count == fin_cells:
                            cell_count = 0
                            fin = False #end of fin

                    else:
                        heat_sink[y,x] = 0
                        cell_count += 1

                        if cell_count == space_cells:
                            cell_count = 0
                            fin = True

    else:
        print("Input heat sink dimensions not evenly divisible into grid")

    return heat_sink

HS = create_HS(6, 1, 20, 3, 2)
a = 1
from Lib.Element import Element

class Simulation:

    _object_list = []

    def __init__(self, ambient_temp = 20, wind_speed = 20, grid_spacing = 0.1, initial_guess = 0, tolerance = False, natural = True):
        self._ambient_temp = ambient_temp
        self._wind_speed = wind_speed
        self._grid_spacing = grid_spacing
        self._initial_guess = initial_guess
        self._tolerance = tolerance
        self._natural = natural

    def add_processor(self, x_dim, y_dim, q = 0.5, k = 150e-3):
        processor = Element(x_dim, y_dim, h = self._grid_spacing, k = k, q = q, amb_temp=self._ambient_temp, initial_guess=self._initial_guess, tolerance=self._tolerance, natural=self._natural)
        self._object_list.append(processor)

    def add_ceramic(self, x_dim, y_dim, k = 230e-3):
        ceramic = Element(x_dim, y_dim, h = self._grid_spacing, k = k, q = 0, amb_temp=self._ambient_temp, initial_guess=self._initial_guess, tolerance=self._tolerance, natural=self._natural)


    def jacobi_solve(self, max_iterations):
        convergence = False
        iteration = 0
        while iteration < max_iterations or convergence is False:
            for element in self._object_list: #runs iterations
                element.jacobi_iteration()

            for element in self._object_list: #ends iterations
                element.iteration_end()

        for element in self._object_list:
            element.finalize_array()
            print(element._avg_temp)
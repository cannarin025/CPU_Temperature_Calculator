from Lib.Simulation import Simulation

sim = Simulation(grid_spacing=0.5, initial_guess=3000) #cannot set grid spacing to 0.5 for some reason (defaults to 0.1)

sim.add_processor(name="CPU", x_dim=14, y_dim=2)
sim.add_ceramic(name = "Casing", x_dim=20, y_dim=4)
sim.add_heat_sink(name="HeatSink", n_fins=5, fin_height=5, fin_width=2, fin_spacing=2)

sim.mount_to_top("CPU", "Casing")
sim.mount_to_top("Casing", "HeatSink")

sim.jacobi_solve(1000)

sim.graph_individual()

a = 1
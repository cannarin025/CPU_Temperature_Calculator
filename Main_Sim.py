from Lib.Simulation import Simulation

sim = Simulation(grid_spacing=0.1, initial_guess=3000) #cannot set grid spacing to 0.5 for some reason (defaults to 0.1)

sim.add_processor(name="CPU", x_dim=14, y_dim=2)
sim.add_ceramic(name = "Casing", x_dim=20, y_dim=4)
sim.add_heat_sink(name="HeatSink", n_fins=10, fin_height=5, fin_width=2, fin_spacing=2)

sim.mount_to_top("CPU", "Casing")
sim.mount_to_top("Casing", "HeatSink")

#sim.graph_system()

#sim.jacobi_solve(100)
sim.gs_solve(10)  # todo: use of nan in heatsink final_temp array is causing issues as final temp values are used to calculate next iteration.

#sim.graph_individual()
sim.graph_system()
a = 1
#sim.save_data()

#todo: Temperature in simulations is skewed left. unsure why. need to fix. Also check initialised values for HS and CPU / ceramic. Not consistent between initial_guess and 0
from Lib.Element import *
from Lib.HeatSink import *

step_size = 1
amb_temp = 20
initial_guess = 5000
max_iterations = 1000

processor = Element(name = "CPU", x_dim=14, y_dim=5, h=step_size, k=150e-3, q=0.5, amb_temp=amb_temp, initial_guess=initial_guess)
ceramic = Element(name = "Casing", x_dim=20, y_dim=10, h = step_size, k = 230e-3, q = 0, amb_temp=amb_temp, initial_guess=initial_guess)
heat_sink = HeatSink(name = "HeatSink", n_fins=8, h = step_size, fin_height=5, fin_width=2, fin_spacing=2, initial_guess=initial_guess)
processor.mount_top(ceramic)
ceramic.mount_top(heat_sink)


#solving via jacobi method
for iteration in range(1000):
    processor.jacobi_iteration()
    ceramic.jacobi_iteration()
    heat_sink.jacobi_iteration()
    processor.iteration_end()
    ceramic.iteration_end()
    heat_sink.iteration_end()

processor.finalize_array()
ceramic.finalize_array()
heat_sink.finalize_array()

#final arrays
processor_result = processor.get_final_temp_array()
ceramic_result = ceramic.get_final_temp_array()
heat_sink_result = heat_sink.get_final_temp_array()

print(processor.get_avg_temp(), "processor avg T")
print(ceramic.get_avg_temp(), "ceramic avg T")
processor.graph_temperature()
processor.save_data()
ceramic.save_data()
ceramic.graph_temperature()
heat_sink.graph_temperature()

print("Done!")
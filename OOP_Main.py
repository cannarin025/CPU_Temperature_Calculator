from Lib.Element import *

step_size = 0.5
amb_temp = 20
initial_guess = 20

processor = Element(name = "CPU", x_dim=14, y_dim=5, h=step_size, k=150e-3, q=0.5, amb_temp=amb_temp, initial_guess=initial_guess)
ceramic = Element(name = "Casing", x_dim=20, y_dim=5, h = step_size, k = 230e-3, q = 0, amb_temp=amb_temp, initial_guess=initial_guess)
processor.mount_top(ceramic)

for i in range(processor.get_initial_x_dim()+1):
    print(processor.get_mounted_top().convert_coordinate(i),"i: ", i)
print(processor.get_mounted_top().convert_coordinate(10))
print(ceramic.get_mounted_bottom().convert_coordinate(13))
pass


# test = Element(x_dim=6, y_dim=3, h = step_size)
# test2 = Element(x_dim=14, y_dim=5, h = step_size)
# processor.mount_top(test)
# processor.mount_bottom(test2)
# processor.mount_top(test)
# processor.mount_bottom(test)

# print(processor.get_mounted_top().convert_coordinate(6))
# print(test.get_mounted_bottom().convert_coordinate(2))

#processor.jacobi_solve(1000)
#result = processor.get_final_temp_array()
#avg_temp = processor.get_avg_temp()
#print(avg_temp)
#print(result)

for iteration in range(500):
    processor.jacobi_iteration()
    ceramic.jacobi_iteration()
    processor.iteration_end()
    ceramic.iteration_end()

processor.finalize_array()
ceramic.finalize_array()

processor_result = processor.get_final_temp_array()
ceramic_result = ceramic.get_final_temp_array()
print(processor.get_avg_temp(), "processor avg T")
print(ceramic.get_avg_temp(), "ceramic avg T")
processor.graph_temperature()
processor.save_data()
ceramic.graph_temperature()

print("Done!")
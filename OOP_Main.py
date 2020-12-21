from lib.Classes import *

step_size = 1
processor = Element(x_dim=14, y_dim=3, h=step_size, k=150e-3, q=0.5, amb_temp=20, initial_guess=20)

test = Element(x_dim=6, y_dim=3, h = step_size)
test2 = Element(x_dim=14, y_dim=5, h = step_size)
processor.mount_top(test)
processor.mount_bottom(test2)
processor.mount_top(test)
processor.mount_bottom(test)

print(processor.get_mounted_top().convert_coordinate(6))
print(test.get_mounted_bottom().convert_coordinate(2))

processor.Jacobi_Solve(1000)
result = processor.get_final_temp_array()
#print(result)
print("Done!")
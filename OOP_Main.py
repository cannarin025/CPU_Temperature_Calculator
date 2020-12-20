from Classes import *

step_size = 0.1
processor = Element(x_dim=14, y_dim=1, h=step_size, k=150e-3, q=0.5, amb_temp=20, initial_guess=20)

test = Element(x_dim=6, y_dim=3, h = step_size)
test2 = Element(x_dim=8, y_dim=2, h = step_size)
processor.mount_top(test)
processor.mount_bottom(test2)
processor.mount_top(test)
processor.mount_bottom(test)

processor.Jacobi_Solve(1000)
result = processor.get_final_temp_array()
#print(result)
print("Done!")
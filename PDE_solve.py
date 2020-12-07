import numpy as np


def Poisson_Solve(y_range, x_range):
    # remember numpy matrices are indexed: matrix[row][col]
    u = np.zeros((y_range, x_range))  # matrix over all space
    print(u)
    b = np.zeros((y_range, 1))
    print(b)
    laplacian_mat = np.zeros((y_range, x_range))

    for i in range(x_range): #rows
        for j in range(y_range): #cols
            if i != 0 and i != y_range - 1 and j != 0 and j != x_range:
                laplacian_mat[i][j] = u[i - 1][j] + u[i][j - 1] + u[i + 1][j] + u[i][j + 1] - 4 * u[i][j]

    return


def Jacobi_Solve(A, b, guess = -1, iterations = 1):
    #var definitions
    if guess == -1:
        guess = np.zeros((np.shape(A)[0], 1))
        print(guess, "guess")
        print()

    if np.shape(A)[0] == np.shape(A)[1]:
        diagonal = np.zeros(np.shape(A))
        T = np.zeros(np.shape(A))

        for i in range(np.shape(A)[0]): #rows
            for j in range(np.shape(A)[1]): #cols
                if i == j:
                    diagonal[i,j] = A[i,j]

                elif i != j:
                    T[i,j] = A[i,j]

        print(diagonal, "diagonal")
        print()
        print(T,"T")
        #getting diagonal and T
        for n in range(iterations):
            diagonal_inv = np.linalg.inv(diagonal)
            next_guess = -1 * np.matmul(diagonal_inv, np.matmul(T, guess)) + np.matmul(diagonal_inv, b)
            guess = next_guess

        x = guess

        return x


    else:
        print("Error, input matrix not square!")

#Poisson_Solve(5, 5)

a = np.matrix([[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,16]])

x = Jacobi_Solve(a,a,-1,1)
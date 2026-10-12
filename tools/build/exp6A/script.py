import numpy as np

# Create arrays in different ways
arr1 = np.array([10, 20, 30, 40, 50])
arr2 = np.arange(1, 11)
arr3 = np.zeros((2, 3))

print("Array from list:", arr1)
print("Array with arange:", arr2)
print("Zeros array:\n", arr3)
print("Shape of arr3:", arr3.shape)

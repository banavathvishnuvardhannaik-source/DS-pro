import pandas as pd
import numpy as np

np.random.seed(7)
data = pd.Series(
    np.random.randn(6),
    index=[
        ["a", "a", "b", "b", "c", "c"],
        [1, 2, 1, 2, 1, 2],
    ],
)

print("MultiIndex Series:")
print(data)

print("\nSelect level 'b':")
print(data["b"])

print("\nSelect item 2 of every group:")
print(data[:, 2])

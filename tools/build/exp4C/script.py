import pandas as pd
import numpy as np

df1 = pd.DataFrame({
    "a": [1, 2, np.nan, 3],
    "b": [4, 5, 6, np.nan],
})

df2 = pd.DataFrame({
    "a": [7, 8, 9, 10],
    "b": [np.nan, 11, 12, 13],
})

print("df1:")
print(df1)
print("\ndf2:")
print(df2)

# Fill the holes of df1 with values from df2
merged = df1.combine_first(df2)
print("\ndf1.combine_first(df2):")
print(merged)

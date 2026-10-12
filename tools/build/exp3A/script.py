import numpy as np
import pandas as pd

data = {
    "A": [1, 2, np.nan],
    "B": [4, np.nan, np.nan],
}
df = pd.DataFrame(data)

print("Original DataFrame:")
print(df)

# Detect missing values
print("\nMissing-value mask:")
print(df.isna())

# Drop rows that contain NaN
df_clean = df.dropna()
print("\nAfter dropna():")
print(df_clean)

# Fill the NaN values with zero
df_filled = df.fillna(0)
print("\nAfter fillna(0):")
print(df_filled)

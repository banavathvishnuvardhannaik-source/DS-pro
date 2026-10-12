import pandas as pd
import numpy as np

np.random.seed(7)
data = pd.Series(
    np.random.randn(6),
    index=[["a", "a", "b", "b", "c", "c"], [1, 2, 1, 2, 1, 2]],
)

# Turn the inner index level into columns
df = data.unstack()
print("After unstack():")
print(df)

# Melt the columns back into the long format
print("\nAfter stack():")
print(df.stack())

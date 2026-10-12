import numpy as np
import pandas as pd

np.random.seed(42)
data = pd.DataFrame(np.random.randn(100, 3), columns=["A", "B", "C"])

# Flag values more than 3 standard units away from the mean
outliers = (data > 3) | (data < -3)

print("Outliers found per column:")
print(outliers.sum())

print("\nRows containing at least one outlier:")
print(data[outliers.any(axis=1)])

import pandas as pd
date_index = pd.date_range(
    start='2026-10-31',
    periods=7,
    freq='ME'
)
print("Generated DatetimeIndex:")
print(date_index)
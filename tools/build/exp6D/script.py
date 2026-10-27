import pandas as pd
p = pd.Period('2026-10', freq='M')
print("Original Period:")
print(p)
print("\nAfter adding 4:")
print(p + 4)
print("\nAfter adding 9:")
print(p + 9)
print("\nAfter subtracting 5:")
print(p - 5)
periods = pd.period_range(
    start='2026-10',
    periods=5,
    freq='M'
)
print("\nRange of Periods:")
print(periods)
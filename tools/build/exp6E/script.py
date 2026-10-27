import pandas as pd
p = pd.Period('2026-10', freq='M')
print("Original Period:")
print(p)
daily_start = p.asfreq('D', how='start')
print("\nMonthly Period converted to Daily (Start):")
print(daily_start)
daily_end = p.asfreq('D', how='end')
print("\nMonthly Period converted to Daily (End):")
print(daily_end)
period_index = pd.period_range(
    start='2026-10',
    periods=3,
    freq='M'
)
print("\nOriginal PeriodIndex:")
print(period_index)
daily_period_index = period_index.asfreq(
    'D',
    how='start'
)
print("\nPeriodIndex converted to Daily Frequency:")
print(daily_period_index)
daily_period_index_end = period_index.asfreq(
    'D',
    how='end'
)
print("\nPeriodIndex converted to Daily Frequency (End):")
print(daily_period_index_end)
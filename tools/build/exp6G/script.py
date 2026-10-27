import pandas as pd
dates = pd.date_range(
    start='2026-10-01 00:00',
    periods=6,
    freq='h'
)
values = [10, 12, 15, 14, 18, 20]
time_series = pd.Series(
    values,
    index=dates
)
print("Original Hourly Time Series:")
print(time_series)
resampled = time_series.resample('3h').mean()
print("\nResampled Time Series - 3 Hour Mean:")
print(resampled)
downsampled = time_series.resample('4h').sum()
print("\nDownsampled Time Series - 4 Hour Sum:")
print(downsampled)
upsampled = time_series.resample('30min').asfreq()
print("\nUpsampled Time Series - 30minute:")
print(upsampled)
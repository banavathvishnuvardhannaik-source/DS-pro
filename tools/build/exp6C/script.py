import pandas as pd
india_dates = pd.date_range(
    start='2026-02-01 10:00',
    periods=3,
    freq='h',
    tz='Asia/Kolkata'
)
print("1. Date Range with Asia/Kolkata Time Zone:")
print(india_dates)
dates = pd.date_range(
    start='2026-02-01 10:00',
    periods=3,
    freq='h'
)
print("\n2. Timezone-naive Date Range:")
print(dates)
localized_dates = dates.tz_localize('Asia/Kolkata')
print("\n3. After Localizing to Asia/Kolkata:")
print(localized_dates)
new_york_dates = localized_dates.tz_convert(
    'America/New_York'
)
print("\n4. Converted to America/New_York:")
print(new_york_dates)
india_series = pd.Series(
    [25, 30, 35],
    index=localized_dates
)
new_york_series = pd.Series(
    [40, 45, 50],
    index=new_york_dates
)
print("\n5. India Time Series:")
print(india_series)
print("\nNew York Time Series:")
print(new_york_series)
combined_series = pd.concat([
    india_series,
    new_york_series
])
print("\n6. Combined Time Series:")
print(combined_series)
import pandas as pd
dates = pd.to_datetime([
    '2026-10-10',
    '2026-11-15',
    '2026-12-20',
    '2027-01-25'
])
sales = pd.Series(
    [1200, 1600, 1900, 2300],
    index=dates
)
print("Original Series:")
print(sales)
period_series = sales.to_period('M')
print("\nSeries converted to Monthly Periods:")
print(period_series)
df = pd.DataFrame(
    {
        'Sales': [1200, 1600, 1900, 2300],
        'Profit': [250, 350, 450, 550]
    },
    index=dates
)
print("\nOriginal DataFrame:")
print(df)
period_df = df.to_period('M')
print("\nDataFrame converted to Monthly Periods:")
print(period_df)
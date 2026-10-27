import pandas as pd
dates=pd.to_datetime([
    '2026-10-01',
    '2026-10-02',
    '2026-10-03',
    '2026-10-04'
])
temperature=[27,31,32,28]
time_series=pd.Series(data=temperature,index=dates)
print("Time series")
print(time_series)
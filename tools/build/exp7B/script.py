import pandas as pd
data = {
    'Department':['DS','DS','AIML','AIML'],
    'Marks':[90,95,96,100],
    'Attendance': [90,85,95,87]
}
df = pd.DataFrame(data)

print("Original DataFrame:")
print(df)
result = df.groupby('Department').aggregate({
    'Marks': ['sum', 'mean', 'std'],
    'Attendance': ['sum', 'mean', 'std']
})
print("\nSummary Statistics:")
print(result)
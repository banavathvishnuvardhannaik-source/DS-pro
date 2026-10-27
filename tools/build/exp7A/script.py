import pandas as pd
data = {
    'Name': ['gani','bala','vishnu','kani'],
    'Department': ['DS','DS','ECE','ECE'],
    'Year': [2,3,3,2],
    'Marks': [99,100,95,98]
}
df = pd.DataFrame(data)
print("Original DataFrame:")
print(df)
print("\n1. Group by Department:")
group1 = df.groupby('Department')
for name, group in group1:
    print("\nDepartment:", name)
    print(group)
print("\nAverage Marks by Department:")
print(df.groupby('Department')['Marks'].mean())
print("\n2. Group by Department and Year:")
group2 = df.groupby(['Department', 'Year'])
for name, group in group2:
    print("\nGroup:", name)
    print(group)
print("\nAverage Marks by Department and Year:")
print(df.groupby(['Department', 'Year'])['Marks'].mean())
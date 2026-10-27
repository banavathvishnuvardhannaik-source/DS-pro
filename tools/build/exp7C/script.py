import pandas as pd
url = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv"
df = pd.read_csv(url)
print("First 5 Records:")
print(df.head())
print("\nDataset Information:")
print(df.info())
print("\nStatistical Summary:")
print(df.describe())
print("\n1. GroupBy using a Single Column:")
group_single = df.groupby('species')['sepal_length'].agg(
    ['count', 'sum', 'mean', 'std', 'min', 'max']
)
print(group_single)
print("\n2. GroupBy using Multiple Columns:")
group_multiple = df.groupby(
    ['species', 'sepal_width']
)['sepal_length'].mean()
print(group_multiple.head(15))
print("\n3. Summary Statistics:")
summary = df.groupby('species').agg({
    'sepal_length': ['mean', 'std', 'min', 'max'],
    'sepal_width': ['mean', 'std', 'min', 'max'],
    'petal_length': ['mean', 'std', 'min', 'max'],
    'petal_width': ['mean', 'std', 'min', 'max']
})
print(summary)
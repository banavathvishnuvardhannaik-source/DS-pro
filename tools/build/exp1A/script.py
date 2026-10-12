import pandas as pd

# Read the iris dataset directly from an online CSV file
url = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv"
df = pd.read_csv(url)

# Save it as a local CSV file
df.to_csv("iris_output.csv", index=False)

print("First five rows of the iris dataset:")
print(df.head())
print()
print("Dataset successfully written to iris_output.csv")
print("Shape:", df.shape)

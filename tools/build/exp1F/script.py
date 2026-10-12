import pandas as pd

student_data = {
    "Roll_No": [101, 102, 103],
    "Name": ["Vish", "Kani", "Shashi"],
    "Department": ["DS", "IT", "CSE"],
    "Percentage": [89, 92, 97],
}

df = pd.DataFrame(student_data)

# Write as a tab-separated text file
df.to_csv("student2.txt", sep="\t", index=False)
print("Student data successfully written to student2.txt\n")

# Read the text file back into a DataFrame
df_read = pd.read_csv("student2.txt", sep="\t")
print("Student data read from the text file:")
print(df_read)

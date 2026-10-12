import pandas as pd

student_data = {
    "Roll_no": [101, 102, 103, 104],
    "Name": ["Mammooty", "DQ", "Tovino", "Basil"],
    "Department": ["Thriller", "Drama", "Sci-Fi", "Comedy"],
    "Ratings": [4, 5, 5, 4],
}

df = pd.DataFrame(student_data)

# Write the DataFrame to a JSON file
df.to_json("student.json", orient="records", indent=4)
print("Successfully written to 'student.json'\n")

# Read the JSON file back into a DataFrame
df_read = pd.read_json("student.json")
print("Data read back from JSON:")
print(df_read)

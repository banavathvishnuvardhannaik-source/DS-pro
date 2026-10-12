import pandas as pd

student_data = {
    "Roll_NO": [101, 102, 103, 104],
    "Name": ["Vishnu", "Kanishka", "Shashank", "Kushvanth"],
    "Department": ["IT", "CSE", "CSD", "DS"],
    "Marks": [92, 98, 95, 76],
}

df = pd.DataFrame(student_data)
df.to_excel("student.xlsx", sheet_name="student_Details", index=False)
print("Data successfully written to student.xlsx\n")

df_read = pd.read_excel("student.xlsx", sheet_name="student_Details")
print("Data read from the Excel file:")
print(df_read)

import pandas as pd

student_data = {
    "Roll_no": [101, 102, 103],
    "Name": ["Vishnu", "Kanishka", "Shashank"],
    "Department": ["IT", "CSE", "CSD"],
    "Marks": [95, 97, 98],
}
course_data = {
    "course_id": ["C101", "C102", "C103"],
    "course_Name": ["Python", "SQL", "Machine Learning"],
    "credit": [9, 8, 9],
}

student_df = pd.DataFrame(student_data)
courses_df = pd.DataFrame(course_data)

# Write both DataFrames into one workbook
with pd.ExcelWriter("college_data.xlsx", engine="openpyxl") as writer:
    student_df.to_excel(writer, sheet_name="students", index=False)
    courses_df.to_excel(writer, sheet_name="courses", index=False)
print("Multiple sheets written to college_data.xlsx\n")

# Read every sheet back at once
excel_data = pd.read_excel("college_data.xlsx", sheet_name=None)
print("Available sheets:", list(excel_data.keys()))
print("\nStudents sheet:")
print(excel_data["students"])
print("\nCourses sheet:")
print(excel_data["courses"])

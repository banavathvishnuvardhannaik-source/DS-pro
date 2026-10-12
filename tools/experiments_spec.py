# ============================================================
# EXPERIMENTS SPEC — single source of truth
# Built from: C:\Users\HP\OneDrive\Desktop\Data-Science
#
# make_videos.py uses this file to:
#   1. execute each section's code and capture the real output
#   2. render the execution videos (assets/videos/*.mp4)
#   3. regenerate js/data.js with the same code + video paths
# ============================================================

EXPERIMENTS_SPEC = [

    # ==================== EXPERIMENT 1 ====================
    {
        "id": 1,
        "number": 1,
        "name": "Data Import & Export with Pandas",
        "youtubeVideo": "https://www.youtube.com/embed/vmEHCJofslg",
        "youtubeLink": "https://www.youtube.com/watch?v=vmEHCJofslg",
        "githubLink": "https://github.com/your-username/ds-lab-experiment-1",
        "summary": (
            "This experiment demonstrates how to bring data from the outside world into "
            "Pandas and export it back again. We work through every major data source a "
            "data scientist meets in practice: CSV files, JSON documents, Excel workbooks "
            "(single and multiple sheets), plain text files, online datasets, live web "
            "APIs and SQL databases. Each section is a complete mini-program that writes "
            "data and reads it back into a DataFrame."
        ),
        "sections": [
            {
                "letter": "A",
                "title": "CSV Files",
                "plot": False,
                "code": '''import pandas as pd

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
''',
            },
            {
                "letter": "B",
                "title": "JSON Files",
                "plot": False,
                "code": '''import pandas as pd

student_data = {
    "Roll_no": [101, 102, 103, 104],
    "Name": ["Mammooty", "DQ", "Tovino", "Basil"],
    "Department": ["Thriller", "Drama", "Sci-Fi", "Comedy"],
    "Ratings": [4, 5, 5, 4],
}

df = pd.DataFrame(student_data)

# Write the DataFrame to a JSON file
df.to_json("student.json", orient="records", indent=4)
print("Successfully written to 'student.json'\\n")

# Read the JSON file back into a DataFrame
df_read = pd.read_json("student.json")
print("Data read back from JSON:")
print(df_read)
''',
            },
            {
                "letter": "C",
                "title": "Data from Web APIs",
                "plot": False,
                "code": '''import pandas as pd
import requests

# 1. Load JSON data straight from a web API
users_url = "https://jsonplaceholder.typicode.com/users"
df_users = pd.read_json(users_url)
print("Users loaded from the web API:")
print(df_users[["id", "name", "username", "email"]].head())
print()

# 2. Query the GitHub API for the latest pandas issues
issues_url = "https://api.github.com/repos/pandas-dev/pandas/issues"
response = requests.get(issues_url)
df_issues = pd.DataFrame(response.json())
print("Latest issues from the pandas repository:")
print(df_issues[["number", "title", "state"]].head(5))
''',
            },
            {
                "letter": "D",
                "title": "Excel Files",
                "plot": False,
                "code": '''import pandas as pd

student_data = {
    "Roll_NO": [101, 102, 103, 104],
    "Name": ["Vishnu", "Kanishka", "Shashank", "Kushvanth"],
    "Department": ["IT", "CSE", "CSD", "DS"],
    "Marks": [92, 98, 95, 76],
}

df = pd.DataFrame(student_data)
df.to_excel("student.xlsx", sheet_name="student_Details", index=False)
print("Data successfully written to student.xlsx\\n")

df_read = pd.read_excel("student.xlsx", sheet_name="student_Details")
print("Data read from the Excel file:")
print(df_read)
''',
            },
            {
                "letter": "E",
                "title": "Multiple Excel Sheets",
                "plot": False,
                "code": '''import pandas as pd

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
print("Multiple sheets written to college_data.xlsx\\n")

# Read every sheet back at once
excel_data = pd.read_excel("college_data.xlsx", sheet_name=None)
print("Available sheets:", list(excel_data.keys()))
print("\\nStudents sheet:")
print(excel_data["students"])
print("\\nCourses sheet:")
print(excel_data["courses"])
''',
            },
            {
                "letter": "F",
                "title": "Text Files",
                "plot": False,
                "code": '''import pandas as pd

student_data = {
    "Roll_No": [101, 102, 103],
    "Name": ["Vish", "Kani", "Shashi"],
    "Department": ["DS", "IT", "CSE"],
    "Percentage": [89, 92, 97],
}

df = pd.DataFrame(student_data)

# Write as a tab-separated text file
df.to_csv("student2.txt", sep="\\t", index=False)
print("Student data successfully written to student2.txt\\n")

# Read the text file back into a DataFrame
df_read = pd.read_csv("student2.txt", sep="\\t")
print("Student data read from the text file:")
print(df_read)
''',
            },
            {
                "letter": "G",
                "title": "Online Datasets",
                "plot": False,
                "code": '''import pandas as pd

# Load a dataset directly from the internet
url = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv"
df = pd.read_csv(url)

print("First five rows of the dataset:")
print(df.head())

print("\\nDataset information:")
print(df.info())

print("\\nNumber of rows and columns:")
print(df.shape)
''',
            },
            {
                "letter": "H",
                "title": "SQL Databases",
                "plot": False,
                "code": '''import sqlite3
import pandas as pd

# Connect to a SQLite database and create a table
conn = sqlite3.connect("students.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS students (id INTEGER, name TEXT)")
cursor.execute("DELETE FROM students")

# Insert records
cursor.execute("INSERT INTO students VALUES (1, 'John')")
cursor.execute("INSERT INTO students VALUES (2, 'Doe')")
conn.commit()

# Read the table into a Pandas DataFrame
df = pd.read_sql_query("SELECT * FROM students", conn)
print("Students table loaded into Pandas:")
print(df)

# Update a record and read again
cursor.execute("UPDATE students SET name='Alice' WHERE id=1")
conn.commit()
print("\\nAfter the update:")
print(pd.read_sql_query("SELECT * FROM students", conn))
conn.close()
''',
            },
        ],
    },

    # ==================== EXPERIMENT 3 ====================
    {
        "id": 3,
        "number": 2,
        "name": "Data Cleaning & Preprocessing",
        "youtubeVideo": "https://www.youtube.com/embed/r-uOLxNrNk8",
        "youtubeLink": "https://www.youtube.com/watch?v=r-uOLxNrNk8",
        "githubLink": "https://github.com/your-username/ds-lab-experiment-3",
        "summary": (
            "Real-world data is messy. This experiment teaches the everyday cleaning "
            "moves of a data scientist: detecting and treating missing values with isna, "
            "dropna and fillna; encoding categorical variables and renaming columns; "
            "spotting statistical outliers; and cleaning raw text with regular "
            "expressions. Each section works on a small self-contained dataset."
        ),
        "sections": [
            {
                "letter": "A",
                "title": "Handling Missing Values",
                "plot": False,
                "code": '''import numpy as np
import pandas as pd

data = {
    "A": [1, 2, np.nan],
    "B": [4, np.nan, np.nan],
}
df = pd.DataFrame(data)

print("Original DataFrame:")
print(df)

# Detect missing values
print("\\nMissing-value mask:")
print(df.isna())

# Drop rows that contain NaN
df_clean = df.dropna()
print("\\nAfter dropna():")
print(df_clean)

# Fill the NaN values with zero
df_filled = df.fillna(0)
print("\\nAfter fillna(0):")
print(df_filled)
''',
            },
            {
                "letter": "B",
                "title": "Encoding & Renaming Columns",
                "plot": False,
                "code": '''import pandas as pd

df = pd.DataFrame({
    "gender": ["male", "female", "male", "female"],
})

# Encode text categories as numbers
df["gender_num"] = df["gender"].map({"male": 0, "female": 1})
print("After encoding:")
print(df)

# Rename a column
df_renamed = df.rename(columns={"gender": "sex"})
print("\\nAfter renaming the column:")
print(df_renamed)
''',
            },
            {
                "letter": "C",
                "title": "Outlier Detection",
                "plot": False,
                "code": '''import numpy as np
import pandas as pd

np.random.seed(42)
data = pd.DataFrame(np.random.randn(100, 3), columns=["A", "B", "C"])

# Flag values more than 3 standard units away from the mean
outliers = (data > 3) | (data < -3)

print("Outliers found per column:")
print(outliers.sum())

print("\\nRows containing at least one outlier:")
print(data[outliers.any(axis=1)])
''',
            },
            {
                "letter": "D",
                "title": "Text Cleaning with Regex",
                "plot": False,
                "code": '''import re

text = "This is \\t a\\n test   of    regex cleaning"

# Split on any whitespace: spaces, tabs or newlines
tokens = re.split(r"\\s+", text.strip())
print("Tokens after splitting on whitespace:")
print(tokens)

# Replace every whitespace run with a single space
cleaned = re.sub(r"\\s+", " ", text).strip()
print("\\nCleaned text:")
print(cleaned)
''',
            },
        ],
    },

    # ==================== EXPERIMENT 4 ====================
    {
        "id": 4,
        "number": 3,
        "name": "Hierarchical Indexing & Reshaping",
        "youtubeVideo": "https://www.youtube.com/embed/vmEHCJofslg",
        "youtubeLink": "https://www.youtube.com/watch?v=vmEHCJofslg",
        "githubLink": "https://github.com/your-username/ds-lab-experiment-4",
        "summary": (
            "Pandas can keep several levels of row labels at the same time. In this "
            "experiment we build a MultiIndex Series, select data across its levels, "
            "reshape tables with stack and unstack, and merge overlapping DataFrames "
            "with combine_first so missing cells are filled from a second source."
        ),
        "sections": [
            {
                "letter": "A",
                "title": "MultiIndex Series",
                "plot": False,
                "code": '''import pandas as pd
import numpy as np

np.random.seed(7)
data = pd.Series(
    np.random.randn(6),
    index=[
        ["a", "a", "b", "b", "c", "c"],
        [1, 2, 1, 2, 1, 2],
    ],
)

print("MultiIndex Series:")
print(data)

print("\\nSelect level 'b':")
print(data["b"])

print("\\nSelect item 2 of every group:")
print(data[:, 2])
''',
            },
            {
                "letter": "B",
                "title": "Stack & Unstack",
                "plot": False,
                "code": '''import pandas as pd
import numpy as np

np.random.seed(7)
data = pd.Series(
    np.random.randn(6),
    index=[["a", "a", "b", "b", "c", "c"], [1, 2, 1, 2, 1, 2]],
)

# Turn the inner index level into columns
df = data.unstack()
print("After unstack():")
print(df)

# Melt the columns back into the long format
print("\\nAfter stack():")
print(df.stack())
''',
            },
            {
                "letter": "C",
                "title": "Combining DataFrames",
                "plot": False,
                "code": '''import pandas as pd
import numpy as np

df1 = pd.DataFrame({
    "a": [1, 2, np.nan, 3],
    "b": [4, 5, 6, np.nan],
})

df2 = pd.DataFrame({
    "a": [7, 8, 9, 10],
    "b": [np.nan, 11, 12, 13],
})

print("df1:")
print(df1)
print("\\ndf2:")
print(df2)

# Fill the holes of df1 with values from df2
merged = df1.combine_first(df2)
print("\\ndf1.combine_first(df2):")
print(merged)
''',
            },
        ],
    },

    # ==================== EXPERIMENT 5 ====================
    {
        "id": 5,
        "number": 4,
        "name": "Data Visualization with Matplotlib & Seaborn",
        "youtubeVideo": "https://www.youtube.com/embed/UO98lJQ3QGI",
        "youtubeLink": "https://www.youtube.com/watch?v=UO98lJQ3QGI",
        "githubLink": "https://github.com/your-username/ds-lab-experiment-5",
        "summary": (
            "A picture is worth a thousand rows. This experiment builds the five "
            "essential charts of exploratory data analysis — line plot, bar plot, "
            "histogram with a density curve, scatter plot and box plot — using "
            "Matplotlib, Pandas plotting and Seaborn, each styled and labelled."
        ),
        "sections": [
            {
                "letter": "A",
                "title": "Line Plot",
                "plot": True,
                "code": '''import matplotlib.pyplot as plt

x = [10, 20, 30, 40]
y = [100, 200, 300, 400]

plt.figure(figsize=(6, 4))
plt.plot(x, y, marker="o", color="#8c1d40", linewidth=2)
plt.title("Line Plot")
plt.xlabel("X-axis")
plt.ylabel("Y-axis")
plt.grid(True)
plt.tight_layout()
plt.show()
''',
            },
            {
                "letter": "B",
                "title": "Bar Plot",
                "plot": True,
                "code": '''import pandas as pd
import matplotlib.pyplot as plt

df = pd.DataFrame({
    "category": ["A", "B", "C"],
    "values": [100, 200, 215],
})

df.plot(kind="bar", x="category", y="values",
        color="#c9a227", legend=False)
plt.title("Bar Plot")
plt.ylabel("Value")
plt.tight_layout()
plt.show()
''',
            },
            {
                "letter": "C",
                "title": "Histogram & Density",
                "plot": True,
                "code": '''import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

np.random.seed(42)
data = np.random.randn(1000)

sns.histplot(data, kde=True, color="#8c1d40")
plt.title("Histogram & Density")
plt.tight_layout()
plt.show()
''',
            },
            {
                "letter": "D",
                "title": "Scatter Plot",
                "plot": True,
                "code": '''import numpy as np
import matplotlib.pyplot as plt

np.random.seed(1)
x = np.random.rand(50)
y = np.random.rand(50)

plt.figure(figsize=(6, 4))
plt.scatter(x, y, s=70, c="#0f766e", alpha=0.75, edgecolors="white")
plt.title("Scatter Plot")
plt.xlabel("X")
plt.ylabel("Y")
plt.tight_layout()
plt.show()
''',
            },
            {
                "letter": "E",
                "title": "Box Plot",
                "plot": True,
                "code": '''import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

np.random.seed(5)
data = np.random.randn(200)

sns.boxplot(x=data, color="#c9a227")
plt.title("Box Plot")
plt.tight_layout()
plt.show()
''',
            },
        ],
    },
    {
        "id": 6,
        "number": 5,
        "name": "NumPy Basics for Data Science",
        "youtubeVideo": "https://www.youtube.com/embed/UO98lJQ3QGI",
        "youtubeLink": "https://www.youtube.com/watch?v=UO98lJQ3QGI",
        "githubLink": "https://github.com/dashboard",
        "summary": (
            "An introduction to NumPy, the core library for numerical computing in "
            "Python. We create arrays in different ways and explore basic arithmetic "
            "operations and statistics on them."
        ),
        "sections": [
            {
                "letter": "A",
                "title": "Creating NumPy Arrays",
                "plot": False,
                "code": '''import numpy as np

# Create arrays in different ways
arr1 = np.array([10, 20, 30, 40, 50])
arr2 = np.arange(1, 11)
arr3 = np.zeros((2, 3))

print("Array from list:", arr1)
print("Array with arange:", arr2)
print("Zeros array:\\n", arr3)
print("Shape of arr3:", arr3.shape)
''',
            },
            {
                "letter": "B",
                "title": "Array Operations",
                "plot": False,
                "code": '''import numpy as np

arr = np.array([2, 4, 6, 8, 10])
print("Original array:", arr)
print("Add 5:", arr + 5)
print("Multiply by 2:", arr * 2)
print("Mean:", arr.mean())
print("Standard deviation:", arr.std())
print("Max:", arr.max(), "Min:", arr.min())
''',
            },
        ],
    },
]

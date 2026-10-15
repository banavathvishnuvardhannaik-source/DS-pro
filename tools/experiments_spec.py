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

EXPERIMENTS_SPEC.extend([
{
        "id": 6,
        "number": 6,
        "name": "Time Series Analysis in Pandas",
        "youtubeVideo": "https://www.youtube.com/embed/vmEHCJofslg",
        "youtubeLink": "https://www.youtube.com/watch?v=vmEHCJofslg",
        "githubLink": "https://github.com/your-username/ds-lab-experiment-6",
        "summary": "This experiment explores date and time handling in Pandas: building time series, generating date ranges, mapping time zones, working with periods and converting frequencies, transforming Series and DataFrames to period-based time indices, and resampling time series by aggregating over different intervals.",
        "sections": [
            {
                "letter": "A",
                "title": "Creating a Time Series",
                "plot": False,
                "code": "import pandas as pd\ndates=pd.to_datetime([\n    '2026-10-01',\n    '2026-10-02',\n    '2026-10-03',\n    '2026-10-04'\n])\ntemperature=[27,31,32,28]\ntime_series=pd.Series(data=temperature,index=dates)\nprint(\"Time series\")\nprint(time_series)"
            },
            {
                "letter": "B",
                "title": "Generating Date Ranges",
                "plot": False,
                "code": "import pandas as pd\ndate_index = pd.date_range(\n    start='2026-10-31',\n    periods=7,\n    freq='ME'\n)\nprint(\"Generated DatetimeIndex:\")\nprint(date_index)"
            },
            {
                "letter": "C",
                "title": "Timezone Localization & Conversion",
                "plot": False,
                "code": "import pandas as pd\nindia_dates = pd.date_range(\n    start='2026-02-01 10:00',\n    periods=3,\n    freq='h',\n    tz='Asia/Kolkata'\n)\nprint(\"1. Date Range with Asia/Kolkata Time Zone:\")\nprint(india_dates)\ndates = pd.date_range(\n    start='2026-02-01 10:00',\n    periods=3,\n    freq='h'\n)\nprint(\"\\n2. Timezone-naive Date Range:\")\nprint(dates)\nlocalized_dates = dates.tz_localize('Asia/Kolkata')\nprint(\"\\n3. After Localizing to Asia/Kolkata:\")\nprint(localized_dates)\nnew_york_dates = localized_dates.tz_convert(\n    'America/New_York'\n)\nprint(\"\\n4. Converted to America/New_York:\")\nprint(new_york_dates)\nindia_series = pd.Series(\n    [25, 30, 35],\n    index=localized_dates\n)\nnew_york_series = pd.Series(\n    [40, 45, 50],\n    index=new_york_dates\n)\nprint(\"\\n5. India Time Series:\")\nprint(india_series)\nprint(\"\\nNew York Time Series:\")\nprint(new_york_series)\ncombined_series = pd.concat([\n    india_series,\n    new_york_series\n])\nprint(\"\\n6. Combined Time Series:\")\nprint(combined_series)"
            },
            {
                "letter": "D",
                "title": "Working with Period Objects",
                "plot": False,
                "code": "import pandas as pd\np = pd.Period('2026-10', freq='M')\nprint(\"Original Period:\")\nprint(p)\nprint(\"\\nAfter adding 4:\")\nprint(p + 4)\nprint(\"\\nAfter adding 9:\")\nprint(p + 9)\nprint(\"\\nAfter subtracting 5:\")\nprint(p - 5)\nperiods = pd.period_range(\n    start='2026-10',\n    periods=5,\n    freq='M'\n)\nprint(\"\\nRange of Periods:\")\nprint(periods)"
            },
            {
                "letter": "E",
                "title": "Period Frequency Conversion (asfreq)",
                "plot": False,
                "code": "import pandas as pd\np = pd.Period('2026-10', freq='M')\nprint(\"Original Period:\")\nprint(p)\ndaily_start = p.asfreq('D', how='start')\nprint(\"\\nMonthly Period converted to Daily (Start):\")\nprint(daily_start)\ndaily_end = p.asfreq('D', how='end')\nprint(\"\\nMonthly Period converted to Daily (End):\")\nprint(daily_end)\nperiod_index = pd.period_range(\n    start='2026-10',\n    periods=3,\n    freq='M'\n)\nprint(\"\\nOriginal PeriodIndex:\")\nprint(period_index)\ndaily_period_index = period_index.asfreq(\n    'D',\n    how='start'\n)\nprint(\"\\nPeriodIndex converted to Daily Frequency:\")\nprint(daily_period_index)\ndaily_period_index_end = period_index.asfreq(\n    'D',\n    how='end'\n)\nprint(\"\\nPeriodIndex converted to Daily Frequency (End):\")\nprint(daily_period_index_end)"
            },
            {
                "letter": "F",
                "title": "Converting Series / DataFrame to Periods",
                "plot": False,
                "code": "import pandas as pd\ndates = pd.to_datetime([\n    '2026-10-10',\n    '2026-11-15',\n    '2026-12-20',\n    '2027-01-25'\n])\nsales = pd.Series(\n    [1200, 1600, 1900, 2300],\n    index=dates\n)\nprint(\"Original Series:\")\nprint(sales)\nperiod_series = sales.to_period('M')\nprint(\"\\nSeries converted to Monthly Periods:\")\nprint(period_series)\ndf = pd.DataFrame(\n    {\n        'Sales': [1200, 1600, 1900, 2300],\n        'Profit': [250, 350, 450, 550]\n    },\n    index=dates\n)\nprint(\"\\nOriginal DataFrame:\")\nprint(df)\nperiod_df = df.to_period('M')\nprint(\"\\nDataFrame converted to Monthly Periods:\")\nprint(period_df)"
            },
            {
                "letter": "G",
                "title": "Resampling Time Series",
                "plot": False,
                "code": "import pandas as pd\ndates = pd.date_range(\n    start='2026-10-01 00:00',\n    periods=6,\n    freq='h'\n)\nvalues = [10, 12, 15, 14, 18, 20]\ntime_series = pd.Series(\n    values,\n    index=dates\n)\nprint(\"Original Hourly Time Series:\")\nprint(time_series)\nresampled = time_series.resample('3h').mean()\nprint(\"\\nResampled Time Series - 3 Hour Mean:\")\nprint(resampled)\ndownsampled = time_series.resample('4h').sum()\nprint(\"\\nDownsampled Time Series - 4 Hour Sum:\")\nprint(downsampled)\nupsampled = time_series.resample('30min').asfreq()\nprint(\"\\nUpsampled Time Series - 30minute:\")\nprint(upsampled)"
            }
        ]
    },
    {
        "id": 7,
        "number": 7,
        "name": "GroupBy and Data Aggregation in Pandas",
        "youtubeVideo": "https://www.youtube.com/embed/vmEHCJofslg",
        "youtubeLink": "https://www.youtube.com/watch?v=vmEHCJofslg",
        "githubLink": "https://github.com/your-username/ds-lab-experiment-7",
        "summary": "This experiment groups and aggregates tabular data in Pandas: grouping by single or multiple keys, calculating per-group means and totals, applying multiple aggregate functions across columns at once, and producing rich summary statistics (count, sum, mean, std, min, max) on the classic iris dataset.",
        "sections": [
            {
                "letter": "A",
                "title": "GroupBy: Single & Multiple Keys",
                "plot": False,
                "code": "import pandas as pd\ndata = {\n    'Name': ['gani','bala','vishnu','kani'],\n    'Department': ['DS','DS','ECE','ECE'],\n    'Year': [2,3,3,2],\n    'Marks': [99,100,95,98]\n}\ndf = pd.DataFrame(data)\nprint(\"Original DataFrame:\")\nprint(df)\nprint(\"\\n1. Group by Department:\")\ngroup1 = df.groupby('Department')\nfor name, group in group1:\n    print(\"\\nDepartment:\", name)\n    print(group)\nprint(\"\\nAverage Marks by Department:\")\nprint(df.groupby('Department')['Marks'].mean())\nprint(\"\\n2. Group by Department and Year:\")\ngroup2 = df.groupby(['Department', 'Year'])\nfor name, group in group2:\n    print(\"\\nGroup:\", name)\n    print(group)\nprint(\"\\nAverage Marks by Department and Year:\")\nprint(df.groupby(['Department', 'Year'])['Marks'].mean())"
            },
            {
                "letter": "B",
                "title": "Aggregate: sum, mean, std across columns",
                "plot": False,
                "code": "import pandas as pd\ndata = {\n    'Department':['DS','DS','AIML','AIML'],\n    'Marks':[90,95,96,100],\n    'Attendance': [90,85,95,87]\n}\ndf = pd.DataFrame(data)\n\nprint(\"Original DataFrame:\")\nprint(df)\nresult = df.groupby('Department').aggregate({\n    'Marks': ['sum', 'mean', 'std'],\n    'Attendance': ['sum', 'mean', 'std']\n})\nprint(\"\\nSummary Statistics:\")\nprint(result)"
            },
            {
                "letter": "C",
                "title": "GroupBy with Aggregations on the Iris Dataset",
                "plot": False,
                "code": "import pandas as pd\nurl = \"https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv\"\ndf = pd.read_csv(url)\nprint(\"First 5 Records:\")\nprint(df.head())\nprint(\"\\nDataset Information:\")\nprint(df.info())\nprint(\"\\nStatistical Summary:\")\nprint(df.describe())\nprint(\"\\n1. GroupBy using a Single Column:\")\ngroup_single = df.groupby('species')['sepal_length'].agg(\n    ['count', 'sum', 'mean', 'std', 'min', 'max']\n)\nprint(group_single)\nprint(\"\\n2. GroupBy using Multiple Columns:\")\ngroup_multiple = df.groupby(\n    ['species', 'sepal_width']\n)['sepal_length'].mean()\nprint(group_multiple.head(15))\nprint(\"\\n3. Summary Statistics:\")\nsummary = df.groupby('species').agg({\n    'sepal_length': ['mean', 'std', 'min', 'max'],\n    'sepal_width': ['mean', 'std', 'min', 'max'],\n    'petal_length': ['mean', 'std', 'min', 'max'],\n    'petal_width': ['mean', 'std', 'min', 'max']\n})\nprint(summary)"
            }
        ]
    }
])


EXPERIMENTS_SPEC.extend([
    {
    "id": 8,
    "number": 8,
    "name": "Sentiment Analysis of Product Reviews",
    "youtubeVideo": "https://www.youtube.com/embed/vmEHCJofslg",
    "youtubeLink": "https://www.youtube.com/watch?v=vmEHCJofslg",
    "githubLink": "https://github.com/your-username/ds-lab-experiment-8",
    "summary": "This experiment performs sentiment analysis on product reviews collected from an HTML page. Section A checks the file system with os, parses reviews.html with BeautifulSoup and exports the reviews to CSV. Section B builds word clouds and labels every review Positive, Neutral or Negative with the VADER sentiment analyzer. Section C measures text statistics (word, character, numeric and stopword counts) using regex and NLTK stopwords. Section D compares the NLTK bundled VADER analyzer with the standalone vaderSentiment library and scores every review. Section E visualizes the sentiment intensity of all reviews with a colored scatter plot and threshold lines.",
    "sections": [
        {
            "letter": "A",
            "title": "Extracting Reviews from an HTML File",
            "plot": False,
            "code": "import os\n\npath = r\"C:\\Users\\HP\\OneDrive\\Desktop\\reviews.html\"\n\nprint(\"Exists:\", os.path.exists(path))\nprint(\"Is file:\", os.path.isfile(path))\nprint(\"Is folder:\", os.path.isdir(path))\n\nimport os\n\nfolder = r\"C:\\Users\\HP\\OneDrive\\Desktop\\reviews.html\"\n\nprint(os.listdir(folder))\n\nfile_path = r\"C:\\Users\\HP\\OneDrive\\Desktop\\reviews.html\\reviews.html\"\n\nwith open(file_path, \"r\", encoding=\"utf-8\") as file:\n    html_content = file.read()\n\nprint(html_content[:500])\n\nimport os\n\ndesktop = r\"C:\\Users\\HP\\OneDrive\\Desktop\"\n\nfor root, dirs, files in os.walk(desktop):\n    for name in files:\n        if name.lower() == \"reviews.html\":\n            print(os.path.join(root, name))\n\nfrom bs4 import BeautifulSoup\nimport pandas as pd\n\nfile_path = r\"C:\\Users\\HP\\OneDrive\\Desktop\\reviews.html\\reviews.html\"\n\nwith open(file_path, \"r\", encoding=\"utf-8\") as file:\n    html_content = file.read()\n\nsoup = BeautifulSoup(html_content, \"html.parser\")\n\nreviews = []\n\nfor review in soup.find_all(\"div\", class_=\"review\"):\n    title = review.find(\"h3\", class_=\"review-title\").get_text(strip=True)\n    text = review.find(\"p\", class_=\"review-text\").get_text(strip=True)\n    rating = review.find(\"span\", class_=\"rating\").get_text(strip=True)\n\n    reviews.append({\n        \"Review Title\": title,\n        \"Review Text\": text,\n        \"Rating\": rating\n    })\n\ndf = pd.DataFrame(reviews)\n\nprint(df)\n\noutput_path = r\"C:\\Users\\HP\\OneDrive\\Desktop\\reviews.html\\extracted_reviews.csv\"\n\ndf.to_csv(output_path, index=False, encoding=\"utf-8-sig\")\n\nprint(\"Reviews extracted successfully!\")\nprint(\"Total reviews:\", len(df))\nprint(\"Saved to:\", output_path)\n"
        },
        {
            "letter": "B",
            "title": "Word Clouds & VADER Sentiment Classification",
            "plot": True,
            "code": "import os\nimport pandas as pd\nimport matplotlib.pyplot as plt\nfrom wordcloud import WordCloud\nfrom vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer\n\n# File paths\nfolder_path = r\"C:\\Users\\HP\\OneDrive\\Desktop\\reviews.html\"\ncsv_path = os.path.join(folder_path, \"product_reviews.csv\")\n\n# Load extracted reviews\ndf = pd.read_csv(csv_path)\n\n# Check and prepare review text\nif \"Review Text\" in df.columns:\n    df[\"review\"] = df[\"Review Text\"].fillna(\"\").astype(str)\nelif \"review\" in df.columns:\n    df[\"review\"] = df[\"review\"].fillna(\"\").astype(str)\nelse:\n    raise ValueError(\n        \"Review text column not found. Available columns: \"\n        + str(df.columns.tolist())\n    )\n\n# Initialize sentiment analyzer\nanalyzer = SentimentIntensityAnalyzer()\n\n# Classify sentiment\ndef classify_sentiment(text):\n    score = analyzer.polarity_scores(text)[\"compound\"]\n\n    if score >= 0.05:\n        return \"Positive\"\n    elif score <= -0.05:\n        return \"Negative\"\n    else:\n        return \"Neutral\"\n\ndf[\"sentiment\"] = df[\"review\"].apply(classify_sentiment)\n\n# Generate WordCloud\ndef generate_wordcloud(text, title, filename):\n    if not text.strip():\n        print(\"No text available for:\", title)\n        return\n\n    cloud = WordCloud(\n        width=1200,\n        height=600,\n        background_color=\"white\",\n        max_words=150,\n        collocations=False\n    ).generate(text)\n\n    plt.figure(figsize=(12, 6))\n    plt.imshow(cloud, interpolation=\"bilinear\")\n    plt.axis(\"off\")\n    plt.title(title)\n    plt.tight_layout()\n\n    output_path = os.path.join(folder_path, filename)\n    plt.savefig(output_path, dpi=300, bbox_inches=\"tight\")\n    plt.show()\n\n    print(\"Saved:\", output_path)\n\n# All reviews WordCloud\nall_text = \" \".join(df[\"review\"])\ngenerate_wordcloud(\n    all_text,\n    \"WordCloud - All Reviews\",\n    \"wordcloud_all.png\"\n)\n\n# Positive reviews WordCloud\npositive_text = \" \".join(\n    df.loc[df[\"sentiment\"] == \"Positive\", \"review\"]\n)\ngenerate_wordcloud(\n    positive_text,\n    \"WordCloud - Positive Reviews\",\n    \"wordcloud_positive.png\"\n)\n\n# Negative reviews WordCloud\nnegative_text = \" \".join(\n    df.loc[df[\"sentiment\"] == \"Negative\", \"review\"]\n)\ngenerate_wordcloud(\n    negative_text,\n    \"WordCloud - Negative Reviews\",\n    \"wordcloud_negative.png\"\n)\n\n# Save analyzed reviews\noutput_csv = os.path.join(\n    folder_path, \"product_reviews_analyzed.csv\"\n)\ndf.to_csv\n\nimport matplotlib.pyplot as plt\n"
        },
        {
            "letter": "C",
            "title": "Text Statistics with Regex & NLTK Stopwords",
            "plot": True,
            "code": "import os\nimport re\nimport pandas as pd\nimport nltk\nimport matplotlib.pyplot as plt\nimport seaborn as sns\nfrom nltk.corpus import stopwords\nfrom collections import Counter\n\nnltk.download(\"stopwords\", quiet=True)\n\nfolder_path = r\"C:\\Users\\HP\\OneDrive\\Desktop\\reviews.html\"\ndf = pd.read_csv(os.path.join(folder_path, \"product_reviews.csv\"))\n\nif \"Review Text\" in df.columns:\n    df[\"review\"] = df[\"Review Text\"].fillna(\"\").astype(str)\nelif \"review\" in df.columns:\n    df[\"review\"] = df[\"review\"].fillna(\"\").astype(str)\nelse:\n    raise ValueError(\"Review text column not found: \" + str(df.columns.tolist()))\n\nstop_words = set(stopwords.words(\"english\"))\n\ndef analyze_review(text):\n    tokens = re.findall(r\"\\b[\\w']+\\b\", text.lower())\n    words = re.findall(r\"\\b[A-Za-z]+\\b\", text)\n    numeric_tokens = re.findall(r\"\\b\\d+(?:\\.\\d+)?\\b\", text)\n\n    stopword_tokens = [\n        token for token in tokens if token in stop_words\n    ]\n\n    return pd.Series({\n        \"word_count\": len(tokens),\n        \"character_count\": len(text),\n        \"numeric_count\": len(numeric_tokens),\n        \"stopword_count\": len(stopword_tokens),\n        \"average_word_length\": (\n            sum(len(word) for word in words) / len(words)\n            if words else 0\n        )\n    })\n\nstatistics = df[\"review\"].apply(analyze_review)\ndf = pd.concat([df, statistics], axis=1)\n\ndf.to_csv(\n    os.path.join(folder_path, \"review_statistics.csv\"),\n    index=False,\n    encoding=\"utf-8-sig\"\n)\n\ncolumns = [\n    (\"stopword_count\", \"Stopword Count\"),\n    (\"numeric_count\", \"Numeric Token Count\"),\n    (\"word_count\", \"Word Count\"),\n    (\"character_count\", \"Character Count\"),\n    (\"average_word_length\", \"Average Word Length\")\n]\n\nfig, axes = plt.subplots(3, 2, figsize=(14, 15))\naxes = axes.flatten()\n\nfor i, (column, title) in enumerate(columns):\n    sns.histplot(\n        data=df,\n        x=column,\n        kde=True,\n        ax=axes[i],\n        bins=20\n    )\n    axes[i].set_title(title)\n    axes[i].set_xlabel(title)\n    axes[i].set_ylabel(\"Number of Reviews\")\n\naxes[-1].axis(\"off\")\nplt.tight_layout()\nplt.savefig(\n    os.path.join(folder_path, \"review_statistics_distributions.png\"),\n    dpi=300\n)\nplt.show()\n\nall_tokens = re.findall(\n    r\"\\b[\\w']+\\b\",\n    \" \".join(df[\"review\"]).lower()\n)\n\nstopword_frequency = Counter(\n    token for token in all_tokens if token in stop_words\n)\n\nprint(\"Top 10 stopwords:\")\nprint(stopword_frequency.most_common(10))\n\nprint(\"\\nDescriptive statistics:\")\nprint(df[\n    [\n        \"stopword_count\",\n        \"numeric_count\",\n        \"word_count\",\n        \"character_count\",\n        \"average_word_length\"\n    ]\n].describe())\n\nprint(\"\\nTotal reviews:\", len(df))\nprint(\"Statistics saved successfully.\")\n"
        },
        {
            "letter": "D",
            "title": "VADER Sentiment with NLTK vs vaderSentiment",
            "plot": True,
            "code": "import os\nimport pandas as pd\nimport nltk\nfrom nltk.sentiment.vader import SentimentIntensityAnalyzer as NLTKVADER\nfrom vaderSentiment.vaderSentiment import (\n    SentimentIntensityAnalyzer as StandaloneVADER\n)\n\nnltk.download(\"vader_lexicon\", quiet=True)\n\nfolder_path = r\"C:\\Users\\HP\\OneDrive\\Desktop\\reviews.html\"\ncsv_path = os.path.join(folder_path, \"product_reviews.csv\")\n\ndf = pd.read_csv(csv_path)\n\nif \"Review Text\" in df.columns:\n    df[\"review\"] = df[\"Review Text\"].fillna(\"\").astype(str)\nelif \"review\" in df.columns:\n    df[\"review\"] = df[\"review\"].fillna(\"\").astype(str)\nelse:\n    raise ValueError(\"Review text column not found: \" + str(df.columns.tolist()))\n\nnltk_analyzer = NLTKVADER()\nvader_analyzer = StandaloneVADER()\n\ndef classify(score):\n    if score >= 0.05:\n        return \"Positive\"\n    elif score <= -0.05:\n        return \"Negative\"\n    return \"Neutral\"\n\nnltk_scores = df[\"review\"].apply(nltk_analyzer.polarity_scores)\n\ndf[\"nltk_positive\"] = nltk_scores.apply(lambda x: x[\"pos\"])\ndf[\"nltk_negative\"] = nltk_scores.apply(lambda x: x[\"neg\"])\ndf[\"nltk_neutral\"] = nltk_scores.apply(lambda x: x[\"neu\"])\ndf[\"nltk_compound\"] = nltk_scores.apply(lambda x: x[\"compound\"])\n\nvader_scores = df[\"review\"].apply(vader_analyzer.polarity_scores)\n\ndf[\"vader_positive\"] = vader_scores.apply(lambda x: x[\"pos\"])\ndf[\"vader_negative\"] = vader_scores.apply(lambda x: x[\"neg\"])\ndf[\"vader_neutral\"] = vader_scores.apply(lambda x: x[\"neu\"])\ndf[\"vader_compound\"] = vader_scores.apply(lambda x: x[\"compound\"])\n\ndf[\"nltk_sentiment\"] = df[\"nltk_compound\"].apply(classify)\ndf[\"vader_sentiment\"] = df[\"vader_compound\"].apply(classify)\n\nprint(df[\n    [\n        \"review\",\n        \"nltk_compound\",\n        \"nltk_sentiment\",\n        \"vader_compound\",\n        \"vader_sentiment\"\n    ]\n].head(10).to_string(index=False))\n\nprint(\"\\nNLTK sentiment distribution:\")\nprint(df[\"nltk_sentiment\"].value_counts())\n\nprint(\"\\nStandalone VADER sentiment distribution:\")\nprint(df[\"vader_sentiment\"].value_counts())\n\noutput_path = os.path.join(\n    folder_path, \"sentiment_analysis_results.csv\"\n)\ndf.to_csv(output_path, index=False, encoding=\"utf-8-sig\")\n\nprint(\"\\nResults saved to:\", output_path)\n"
        },
        {
            "letter": "E",
            "title": "Sentiment Intensity Visualization",
            "plot": True,
            "code": "import os\nimport pandas as pd\nimport matplotlib.pyplot as plt\nimport seaborn as sns\n\nfolder_path = r\"C:\\Users\\HP\\OneDrive\\Desktop\\reviews.html\"\ncsv_path = os.path.join(folder_path, \"sentiment_analysis_results.csv\")\n\ndf = pd.read_csv(csv_path)\n\ndf[\"vader_compound\"] = pd.to_numeric(\n    df[\"vader_compound\"], errors=\"coerce\"\n)\n\ndf = df.dropna(subset=[\"vader_compound\"]).reset_index(drop=True)\n\ndf[\"review_index\"] = range(1, len(df) + 1)\n\npalette = {\n    \"Positive\": \"green\",\n    \"Negative\": \"red\",\n    \"Neutral\": \"gray\"\n}\n\nplt.figure(figsize=(14, 7))\n\nsns.scatterplot(\n    data=df,\n    x=\"review_index\",\n    y=\"vader_compound\",\n    hue=\"vader_sentiment\",\n    palette=palette,\n    s=70,\n    alpha=0.8\n)\n\nplt.axhline(\n    y=0.05, color=\"green\", linestyle=\"--\",\n    label=\"Positive threshold\"\n)\nplt.axhline(\n    y=-0.05, color=\"red\", linestyle=\"--\",\n    label=\"Negative threshold\"\n)\nplt.axhline(\n    y=0, color=\"black\", linestyle=\":\",\n    label=\"Neutral reference\"\n)\n\nplt.ylim(-1.05, 1.05)\nplt.xlabel(\"Review Index\")\nplt.ylabel(\"VADER Compound Sentiment Score\")\nplt.title(\"Sentiment Intensity of Product Reviews\")\nplt.legend(loc=\"best\")\nplt.grid(alpha=0.25)\nplt.tight_layout()\n\noutput_path = os.path.join(\n    folder_path, \"sentiment_intensity_scatter.png\"\n)\nplt.savefig(output_path, dpi=300)\nplt.show()\n\nprint(\"Scatter intensity plot saved successfully.\")\nprint(\"Saved to:\", output_path)\n"
        }
    ]
},
]);

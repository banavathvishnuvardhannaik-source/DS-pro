import sqlite3
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
print("\nAfter the update:")
print(pd.read_sql_query("SELECT * FROM students", conn))
conn.close()

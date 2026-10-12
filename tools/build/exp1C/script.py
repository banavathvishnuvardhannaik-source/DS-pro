import pandas as pd
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

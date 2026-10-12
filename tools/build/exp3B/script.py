import pandas as pd

df = pd.DataFrame({
    "gender": ["male", "female", "male", "female"],
})

# Encode text categories as numbers
df["gender_num"] = df["gender"].map({"male": 0, "female": 1})
print("After encoding:")
print(df)

# Rename a column
df_renamed = df.rename(columns={"gender": "sex"})
print("\nAfter renaming the column:")
print(df_renamed)

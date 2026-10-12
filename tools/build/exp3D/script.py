import re

text = "This is \t a\n test   of    regex cleaning"

# Split on any whitespace: spaces, tabs or newlines
tokens = re.split(r"\s+", text.strip())
print("Tokens after splitting on whitespace:")
print(tokens)

# Replace every whitespace run with a single space
cleaned = re.sub(r"\s+", " ", text).strip()
print("\nCleaned text:")
print(cleaned)

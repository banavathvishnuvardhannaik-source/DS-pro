import os

path = r"C:\Users\HP\OneDrive\Desktop\reviews.html"

print("Exists:", os.path.exists(path))
print("Is file:", os.path.isfile(path))
print("Is folder:", os.path.isdir(path))

import os

folder = r"C:\Users\HP\OneDrive\Desktop\reviews.html"

print(os.listdir(folder))

file_path = r"C:\Users\HP\OneDrive\Desktop\reviews.html\reviews.html"

with open(file_path, "r", encoding="utf-8") as file:
    html_content = file.read()

print(html_content[:500])

import os

desktop = r"C:\Users\HP\OneDrive\Desktop"

for root, dirs, files in os.walk(desktop):
    for name in files:
        if name.lower() == "reviews.html":
            print(os.path.join(root, name))

from bs4 import BeautifulSoup
import pandas as pd

file_path = r"C:\Users\HP\OneDrive\Desktop\reviews.html\reviews.html"

with open(file_path, "r", encoding="utf-8") as file:
    html_content = file.read()

soup = BeautifulSoup(html_content, "html.parser")

reviews = []

for review in soup.find_all("div", class_="review"):
    title = review.find("h3", class_="review-title").get_text(strip=True)
    text = review.find("p", class_="review-text").get_text(strip=True)
    rating = review.find("span", class_="rating").get_text(strip=True)

    reviews.append({
        "Review Title": title,
        "Review Text": text,
        "Rating": rating
    })

df = pd.DataFrame(reviews)

print(df)

output_path = r"C:\Users\HP\OneDrive\Desktop\reviews.html\extracted_reviews.csv"

df.to_csv(output_path, index=False, encoding="utf-8-sig")

print("Reviews extracted successfully!")
print("Total reviews:", len(df))
print("Saved to:", output_path)

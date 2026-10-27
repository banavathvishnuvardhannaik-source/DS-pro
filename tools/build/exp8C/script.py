import os
import re
import pandas as pd
import nltk
import matplotlib.pyplot as plt
import seaborn as sns
from nltk.corpus import stopwords
from collections import Counter

nltk.download("stopwords", quiet=True)

folder_path = r"C:\Users\HP\OneDrive\Desktop\reviews.html"
df = pd.read_csv(os.path.join(folder_path, "product_reviews.csv"))

if "Review Text" in df.columns:
    df["review"] = df["Review Text"].fillna("").astype(str)
elif "review" in df.columns:
    df["review"] = df["review"].fillna("").astype(str)
else:
    raise ValueError("Review text column not found: " + str(df.columns.tolist()))

stop_words = set(stopwords.words("english"))

def analyze_review(text):
    tokens = re.findall(r"\b[\w']+\b", text.lower())
    words = re.findall(r"\b[A-Za-z]+\b", text)
    numeric_tokens = re.findall(r"\b\d+(?:\.\d+)?\b", text)

    stopword_tokens = [
        token for token in tokens if token in stop_words
    ]

    return pd.Series({
        "word_count": len(tokens),
        "character_count": len(text),
        "numeric_count": len(numeric_tokens),
        "stopword_count": len(stopword_tokens),
        "average_word_length": (
            sum(len(word) for word in words) / len(words)
            if words else 0
        )
    })

statistics = df["review"].apply(analyze_review)
df = pd.concat([df, statistics], axis=1)

df.to_csv(
    os.path.join(folder_path, "review_statistics.csv"),
    index=False,
    encoding="utf-8-sig"
)

columns = [
    ("stopword_count", "Stopword Count"),
    ("numeric_count", "Numeric Token Count"),
    ("word_count", "Word Count"),
    ("character_count", "Character Count"),
    ("average_word_length", "Average Word Length")
]

fig, axes = plt.subplots(3, 2, figsize=(14, 15))
axes = axes.flatten()

for i, (column, title) in enumerate(columns):
    sns.histplot(
        data=df,
        x=column,
        kde=True,
        ax=axes[i],
        bins=20
    )
    axes[i].set_title(title)
    axes[i].set_xlabel(title)
    axes[i].set_ylabel("Number of Reviews")

axes[-1].axis("off")
plt.tight_layout()
plt.savefig(
    os.path.join(folder_path, "review_statistics_distributions.png"),
    dpi=300
)
plt.show()

all_tokens = re.findall(
    r"\b[\w']+\b",
    " ".join(df["review"]).lower()
)

stopword_frequency = Counter(
    token for token in all_tokens if token in stop_words
)

print("Top 10 stopwords:")
print(stopword_frequency.most_common(10))

print("\nDescriptive statistics:")
print(df[
    [
        "stopword_count",
        "numeric_count",
        "word_count",
        "character_count",
        "average_word_length"
    ]
].describe())

print("\nTotal reviews:", len(df))
print("Statistics saved successfully.")

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.savefig('plot.png', dpi=150, bbox_inches='tight', facecolor='white')

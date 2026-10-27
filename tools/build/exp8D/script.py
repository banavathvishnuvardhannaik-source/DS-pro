import os
import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer as NLTKVADER
from vaderSentiment.vaderSentiment import (
    SentimentIntensityAnalyzer as StandaloneVADER
)

nltk.download("vader_lexicon", quiet=True)

folder_path = r"C:\Users\HP\OneDrive\Desktop\reviews.html"
csv_path = os.path.join(folder_path, "product_reviews.csv")

df = pd.read_csv(csv_path)

if "Review Text" in df.columns:
    df["review"] = df["Review Text"].fillna("").astype(str)
elif "review" in df.columns:
    df["review"] = df["review"].fillna("").astype(str)
else:
    raise ValueError("Review text column not found: " + str(df.columns.tolist()))

nltk_analyzer = NLTKVADER()
vader_analyzer = StandaloneVADER()

def classify(score):
    if score >= 0.05:
        return "Positive"
    elif score <= -0.05:
        return "Negative"
    return "Neutral"

nltk_scores = df["review"].apply(nltk_analyzer.polarity_scores)

df["nltk_positive"] = nltk_scores.apply(lambda x: x["pos"])
df["nltk_negative"] = nltk_scores.apply(lambda x: x["neg"])
df["nltk_neutral"] = nltk_scores.apply(lambda x: x["neu"])
df["nltk_compound"] = nltk_scores.apply(lambda x: x["compound"])

vader_scores = df["review"].apply(vader_analyzer.polarity_scores)

df["vader_positive"] = vader_scores.apply(lambda x: x["pos"])
df["vader_negative"] = vader_scores.apply(lambda x: x["neg"])
df["vader_neutral"] = vader_scores.apply(lambda x: x["neu"])
df["vader_compound"] = vader_scores.apply(lambda x: x["compound"])

df["nltk_sentiment"] = df["nltk_compound"].apply(classify)
df["vader_sentiment"] = df["vader_compound"].apply(classify)

print(df[
    [
        "review",
        "nltk_compound",
        "nltk_sentiment",
        "vader_compound",
        "vader_sentiment"
    ]
].head(10).to_string(index=False))

print("\nNLTK sentiment distribution:")
print(df["nltk_sentiment"].value_counts())

print("\nStandalone VADER sentiment distribution:")
print(df["vader_sentiment"].value_counts())

output_path = os.path.join(
    folder_path, "sentiment_analysis_results.csv"
)
df.to_csv(output_path, index=False, encoding="utf-8-sig")

print("\nResults saved to:", output_path)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.savefig('plot.png', dpi=150, bbox_inches='tight', facecolor='white')

import pandas as pd

df = pd.read_csv(
    "Resume-projects/Financial sentimental analyser/data/all-data.csv",
    encoding="latin1",
    header=None,
    names=["label", "text"]
)

print(df.head())
print(df.shape)
print(df.info())
print(df["label"].value_counts())

print(df.isna().sum())
df = df.drop_duplicates()
print(df["label"].value_counts())
print(df.shape)
print(df.sample(5))

word_count = []
for sentence in df["text"]:
    word_count.append(len(sentence.split()))
df["word_count"] = word_count    

print(df)
print(df.groupby("label")["word_count"].mean())
print(df["word_count"].min())
print(df["word_count"].max())

print(df.sort_values("word_count"))



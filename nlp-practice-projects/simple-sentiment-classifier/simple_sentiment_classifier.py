# Simple Sentiment Classifier
# This project classifies short sentences as positive, negative, or neutral using TF-IDF and Logistic Regression.

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


data = {
    "text": [
        # positive
        "I loved this product",
        "This was amazing",
        "The quality is excellent",
        "I had a great experience",
        "The service was very good",
        "I am happy with my purchase",
        "This exceeded my expectations",
        "The product worked perfectly",
        "I would recommend this to others",
        "Everything was smooth and easy",

        # negative
        "I hated this product",
        "This was terrible",
        "The quality is very poor",
        "I had a bad experience",
        "The service was disappointing",
        "I am unhappy with my purchase",
        "This did not meet my expectations",
        "The product broke quickly",
        "I would not recommend this to others",
        "Everything was frustrating and difficult",

        # neutral
        "The product arrived today",
        "The package contains one item",
        "It is available in two colors",
        "The order was placed yesterday",
        "The product has a simple design",
        "The store opens at nine",
        "The item is made of plastic",
        "The delivery took three days",
        "The box includes a user manual",
        "The product is listed on the website"
    ],
    "label": [
        # positive
        "positive", "positive", "positive", "positive", "positive",
        "positive", "positive", "positive", "positive", "positive",

        # negative
        "negative", "negative", "negative", "negative", "negative",
        "negative", "negative", "negative", "negative", "negative",

        # neutral
        "neutral", "neutral", "neutral", "neutral", "neutral",
        "neutral", "neutral", "neutral", "neutral", "neutral"
    ]
}

df = pd.DataFrame(data)
X = df["text"]
y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(X,y, test_size= 0.2, random_state = 45, stratify = y)

vectorizer = TfidfVectorizer()
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

model = LogisticRegression()
model.fit(X_train_tfidf, y_train)
predictions = model.predict(X_test_tfidf)

print(f"Accuracy: {accuracy_score(y_test, predictions)}")
print(f"Classification-report: {classification_report(y_test, predictions)}")
print(f"Confusion-matrix: {confusion_matrix(y_test, predictions)}")

testing = {"sample_text" : 
           ["I really enjoyed using this",
            "This was a waste of money",
            "The item arrived in a box",
            "The quality was okay"
            ,"I would never buy this again"], 
            "sample_label" : 
            ["positive", 
             "negative",
             "neutral", 
             "neutral", 
             "negative"]}

testing_tfidf = vectorizer.transform(testing["sample_text"])
sample_predictions = model.predict(testing_tfidf)
df_sample = pd.DataFrame(testing)
X_sample = df_sample["sample_text"]
y_sample = df_sample["sample_label"]
print(f"Accuracy: {accuracy_score(y_sample, sample_predictions)}")
print(f"Classification-report: {classification_report(y_sample, sample_predictions)}")
print(f"Confusion-matrix: {confusion_matrix(y_sample, sample_predictions)}")
results = pd.DataFrame({
    "sentences" : X_sample,
    "actual_label" : y_sample,
    "predicted_label" : sample_predictions
})

results["correct"] = results["actual_label"] ==  results["predicted_label"]

print(results.to_string())






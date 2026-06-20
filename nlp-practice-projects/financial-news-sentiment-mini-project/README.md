# Financial News Sentiment Mini Project

## Project Overview

This is a beginner NLP mini project that classifies short financial news-style sentences as **positive**, **negative**, or **neutral**.

The goal of this project was to practice applying the NLP machine learning workflow to financial/business text before building a larger resume-level financial sentiment analyzer.

## Tools Used

* Python
* pandas
* scikit-learn
* TF-IDF Vectorization
* Logistic Regression

## Dataset

I created a small manual dataset with 30 financial/business sentences:

* 10 positive sentences
* 10 negative sentences
* 10 neutral sentences

Each row contains:

* `text`: the financial sentence
* `label`: the sentiment category

## Project Workflow

1. Created a labeled financial sentiment dataset
2. Separated the text column as `X` and the label column as `y`
3. Split the data into training and testing sets
4. Converted financial text into numerical TF-IDF features
5. Used unigrams and bigrams to capture single words and two-word financial phrases
6. Trained a Logistic Regression classification model
7. Predicted sentiment labels for test data
8. Evaluated the model using accuracy, classification report, and confusion matrix
9. Tested the model on custom financial sentences

## Results and Insights

The model was able to follow the full NLP classification workflow and make predictions on financial-style sentences.

One important insight was that financial sentiment is more context-dependent than normal sentiment. Words like “increased” may be positive in one sentence, such as revenue increasing, but negative in another sentence, such as costs increasing.

Another insight was that two-word phrases are useful in financial text. Phrases like “revenue growth,” “higher costs,” “weaker demand,” and “full year guidance” can give the model more meaningful signals than single words alone.

The model also showed that small datasets have limitations. Since the dataset is manually created and only contains 30 rows, the model may not generalize well to real financial news. It can make mistakes on mixed sentences where both positive and negative signals appear.

## Key Learnings

Through this project, I learned:

* How to apply NLP classification to financial text
* How financial sentiment differs from regular product or review sentiment
* How to use TF-IDF with unigrams and bigrams
* How to train a Logistic Regression model for text classification
* How to evaluate a model using accuracy, precision, recall, F1-score, and confusion matrix
* How to test a trained model on custom financial sentences
* Why dataset size and context matter in financial sentiment analysis

## Limitations

* The dataset is manually created and very small
* The model is only for practice and not ready for real-world financial analysis
* The model may struggle with mixed financial statements
* The model does not understand financial context deeply
* Real financial sentiment analysis needs a larger labeled dataset

## Next Steps

Possible improvements:

* Use a real financial sentiment dataset
* Add more examples for each class
* Include more mixed financial sentences
* Compare different models such as Naive Bayes or Linear SVM
* Improve preprocessing for financial text
* Build a full Financial Sentiment Analyzer as a resume-level project

## Conclusion

This project helped me practice applying NLP and machine learning to financial text. I learned how to classify financial sentences into positive, negative, and neutral categories using TF-IDF features and a Logistic Regression model.

This mini project is a foundation for building a stronger Financial Sentiment Analyzer using a real dataset.

# Simple Sentiment Classifier

## Project Overview

This is a beginner NLP practice project that classifies short text sentences as **positive**, **negative**, or **neutral**.

The goal of this project was to practice the full NLP machine learning workflow, from preparing text data to training and evaluating a classification model.

## Tools Used

* Python
* pandas
* scikit-learn
* TF-IDF Vectorization
* Logistic Regression

## Dataset

I created a small manual dataset with 30 short sentences:

* 10 positive sentences
* 10 negative sentences
* 10 neutral sentences

Each row contains:

* `text`: the sentence
* `label`: the sentiment category

## Project Workflow

1. Created a small labeled sentiment dataset
2. Separated the text column as `X` and the label column as `y`
3. Split the data into training and testing sets
4. Converted text into numerical features using TF-IDF
5. Trained a Logistic Regression classification model
6. Predicted sentiment labels for test data
7. Evaluated the model using accuracy, classification report, and confusion matrix
8. Tested the model on custom new sentences

## Results and Insights

The model was able to classify some simple positive, negative, and neutral sentences correctly.

However, because the dataset is very small, the model does not always understand more complex sentences. For example, some sentences with words like “quality” or “buy” may be misclassified because the model is learning from limited examples.

This showed me that NLP models need enough good-quality training data to make reliable predictions.

## Key Learnings

Through this project, I learned:

* How text data is converted into numbers before being used by a machine learning model
* Why TF-IDF is useful for representing text
* How to train a classification model using text features
* How to compare actual labels with predicted labels
* Why accuracy alone is not always enough to judge a model
* How to test a trained model on new custom sentences

## Limitations

* The dataset is manually created and very small
* The model is only for practice and not ready for real-world use
* The model may misclassify sentences that have mixed or unclear sentiment
* A larger real dataset would improve performance

## Next Steps

Possible improvements:

* Use a larger real-world sentiment dataset
* Add more varied examples for each sentiment class
* Try different models such as Naive Bayes or Linear SVM
* Use n-grams to capture phrases like “not good” or “not recommend”
* Build a stronger financial sentiment analyzer using real financial text data

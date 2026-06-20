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

The model was able to follow the full NLP classification workflow and make predictions on both test data and custom sentences.

One important insight was that the model works better on simple sentences that use words similar to the training examples. For example, sentences with clear positive or negative words were easier for the model to classify.

The model struggled with some custom sentences because the dataset is very small. For example, a sentence like “The quality was okay” can be confusing because the word “quality” appears in both positive and negative training examples. The model does not truly understand meaning like a human. It learns patterns from the words it has seen.

This helped me understand that model performance depends heavily on the quality and size of the dataset. A small manual dataset is useful for practice, but a real-world NLP project needs more examples, better variety, and stronger evaluation.

Another insight was that accuracy alone is not enough. It is important to check precision, recall, F1-score, and the confusion matrix to understand where the model is making mistakes.

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
* A larger real-world dataset would improve performance

## Next Steps

Possible improvements:

* Use a larger real-world sentiment dataset
* Add more varied examples for each sentiment class
* Try different models such as Naive Bayes or Linear SVM
* Use n-grams to capture phrases like “not good” or “not recommend”
* Build a stronger financial sentiment analyzer using real financial text data

## Conclusion

This project helped me practice the basic NLP machine learning pipeline from start to finish. I learned how to convert text into numerical TF-IDF features, train a classification model, evaluate predictions, and test the model on new sentences.

This project is a foundation for building larger NLP projects such as a financial sentiment analyzer or resume matcher.

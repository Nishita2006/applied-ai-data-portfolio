# Insights from NumPy Student Marks Analyzer

## 1. Priya had the highest average score

The student with the highest average score was **Priya**, with an average score of **96.75**.

Her total score was **387**, which was the highest total score in the dataset.

## 2. Meera had the lowest average score

The student with the lowest average score was **Meera**, with an average score of **49.50**.

Meera also had scores below 60 in multiple subjects, making her one of the students who may need additional academic support.

## 3. Seven students passed and three students failed

Using the rule `Average Score >= 70` as Pass:

* **7 students passed**
* **3 students failed**

The students who failed were:

* Sara
* Meera
* David

## 4. History had the highest subject average

The subject-wise average scores were:

* Math: **77.70**
* Science: **78.70**
* English: **79.30**
* History: **79.50**

History had the highest subject average score, while Math had the lowest subject average score.

## 5. Sara and Meera scored below 60 in at least one subject

Using boolean masking, the students who had at least one subject score below 60 were:

* Sara
* Meera

This helped identify students who may need support in specific subjects.

## 6. Several scores were above 90

The scores above 90 were:

```text
95, 92, 96, 94, 92, 95, 98, 96, 94, 99
```

These high scores were mainly from top-performing students such as Aman, Ananya, and Priya.

## 7. The score distribution had a median of 81.50

The percentile analysis showed:

* 25th percentile: **69.50**
* 50th percentile / median: **81.50**
* 75th percentile: **90.50**

This means half of all subject scores were below 81.50 and half were above 81.50.

## 8. Bonus-adjusted scores were clipped at 100

Subject-wise bonus marks were added using broadcasting:

* Math: +2
* Science: +3
* English: +2
* History: +1

After adding bonus marks, some scores crossed 100. `np.clip()` was used to keep all scores between 0 and 100.

For example, Priya’s bonus-adjusted scores became:

```text
100, 99, 96, 100
```

## 9. Priya also had the highest weighted score

Weighted scores were calculated using these subject weights:

* Math: 30%
* Science: 30%
* English: 25%
* History: 15%

The highest weighted score was **96.55**, achieved by **Priya**.

The lowest weighted score was **49.70**, achieved by **Meera**.

## Summary

This project helped me practice core NumPy skills such as array creation, axis-based calculations, boolean masking, broadcasting, clipping, percentile analysis, weighted scoring using matrix multiplication, and saving/loading NumPy arrays.

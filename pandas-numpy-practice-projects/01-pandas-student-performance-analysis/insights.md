# Insights from Student Performance Analysis

## 1. Most students passed based on average score

After cleaning the dataset and removing duplicates, the final dataset had **14 students**.

Using the rule `Average_Score >= 70` as Pass, **11 students passed** and **3 students failed**.

## 2. Performance levels were mixed across students

The performance level distribution was:

- **Excellent:** 4 students
- **Good:** 3 students
- **Average:** 3 students
- **Needs Improvement:** 4 students

This shows that while many students performed well, there is still a clear group that may need academic support.

## 3. Chicago had the highest average score by city

Average score by city:

- **Chicago:** 91.00
- **Madison:** 83.33
- **Dallas:** 76.83
- **Boston:** 65.09

Chicago had the highest average score, while Boston had the lowest average score.

## 4. Female students had a higher average score in this dataset

Average score by gender:

- **Female:** 89.53
- **Male:** 67.80

In this sample dataset, female students had a higher average score than male students.

## 5. Parent education showed a clear difference in average score

Average score by parent education level:

- **Master:** 91.82
- **Bachelor:** 84.52
- **High School:** 62.17

Students whose parents had a Master’s degree had the highest average score, while students whose parents had a High School education level had the lowest average score.

## 6. Science had the highest subject average

Subject-wise average scores:

- **Science:** 80.82
- **English:** 80.34
- **Math:** 79.50

Science had the highest average score, while Math had the lowest average score.

## 7. Internet access was linked with higher average scores

Average score by internet access:

- **Yes:** 88.47
- **No:** 65.36

Students with internet access had a much higher average score than students without internet access in this dataset.

## 8. Study category showed a strong performance difference

Average score by study category:

- **High Study:** 93.75
- **Medium Study:** 81.68
- **Low Study:** 58.78

Students in the High Study category had the strongest performance, while students in the Low Study category had the weakest performance.

## 9. Top 5 students by average score

The top 5 students were:

1. **Ananya** — 97.00
2. **Meera** — 95.00
3. **Sophia** — 93.00
4. **Riya** — 90.00
5. **Nisha** — 87.67

All top 5 students were either in the High Study or Medium Study category.

## 10. At-risk students were identified using score and attendance

Students were considered at risk if they had an `Average_Score < 70` or `Attendance < 75`.

The at-risk students were:

- **John** — Average Score: 60.00, Attendance: 65
- **David** — Average Score: 50.00, Attendance: 55
- **Arjun** — Average Score: 66.33, Attendance: 70

These students may need additional academic support or attendance intervention.

## Summary

This project helped me practice a full beginner-level Pandas workflow, including loading data, checking missing values, filling missing data, removing duplicates, creating new columns, grouping data, sorting values, filtering rows, and writing insights from the analysis.
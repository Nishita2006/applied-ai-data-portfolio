# Student Performance Analysis using Pandas

## Project Overview

This project analyzes a student performance dataset using Pandas. The goal of the project is to practice core data analysis skills including data loading, inspection, cleaning, feature creation, grouping, filtering, and basic insight generation.

This is a beginner-friendly Pandas project created as part of my Python, Pandas, NumPy, and machine learning learning journey.

## Dataset Description

The dataset contains student-level information such as:

* Student ID
* Name
* Gender
* Age
* City
* Study hours
* Attendance
* Math score
* Science score
* English score
* Internet access
* Parent education level

The raw dataset intentionally includes missing values and duplicate records so that data cleaning steps can be practiced.

## Project Steps

The project follows these steps:

1. Load the raw CSV file using Pandas
2. Inspect the dataset using `head()`, `info()`, `describe()`, `index`, and `columns`
3. Check missing values using `isna()` and `isna().sum()`
4. Fill missing values using column means
5. Check and remove duplicate records
6. Create new columns:

   * `Total_Score`
   * `Average_Score`
   * `Result`
   * `Performance_Level`
   * `Attendance_Category`
   * `Study_Category`
7. Analyze student performance using grouping, filtering, and sorting
8. Identify top-performing and at-risk students
9. Save the cleaned dataset as a new CSV file

## Skills Practiced

* Pandas DataFrames
* Reading CSV files
* Writing CSV files
* Data inspection
* Missing value handling
* Duplicate removal
* Column creation
* `apply()` and lambda functions
* Conditional logic
* `groupby()`
* Sorting with `sort_values()`
* Filtering rows based on conditions
* Basic exploratory data analysis

## Key Questions Answered

This project answers questions such as:

* How many students passed or failed?
* What are the different performance levels?
* Which city has the highest average score?
* How does average score vary by gender?
* How does parent education relate to average score?
* Which subject has the highest or lowest average score?
* How does internet access relate to student performance?
* Which students are in the top 5 by average score?
* Which students may be at risk based on low scores or low attendance?

## Files in This Project

```text
01-pandas-student-performance-analysis/
│
├── data/
│   ├── student_performance_raw.csv
│   └── student_performance_cleaned.csv
│
├── student_analysis.py
├── README.md
└── insights.md
```

## How to Run the Project

From the root folder of the repository, run:

```bash
python pandas-numpy-practice-projects/01-pandas-student-performance-analysis/student_analysis.py
```

## Output

The script prints data inspection results, cleaning summaries, performance analysis, top students, and at-risk students. It also saves a cleaned CSV file in the `data` folder.

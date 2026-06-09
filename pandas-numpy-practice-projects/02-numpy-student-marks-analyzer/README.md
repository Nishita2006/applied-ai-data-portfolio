# NumPy Student Marks Analyzer

## Project Overview

This project analyzes student marks using only NumPy. The goal is to practice numerical computing concepts such as arrays, axes, aggregation, boolean masking, broadcasting, clipping, percentiles, weighted scores, and saving/loading NumPy arrays.

This is part of my Python, Pandas, NumPy, and machine learning learning journey.

## Dataset Structure

The project uses a manually created NumPy array of student marks.

* Rows represent students
* Columns represent subjects

The marks array has a shape of `(10, 4)`, meaning:

* 10 students
* 4 subjects

Subjects included:

* Math
* Science
* English
* History

## Skills Practiced

* Creating NumPy arrays
* Checking array shape, size, dimensions, and data type
* Student-wise aggregation using `axis=1`
* Subject-wise aggregation using `axis=0`
* Finding maximum and minimum values
* Using `argmax()` and `argmin()`
* Creating pass/fail labels using conditional logic
* Counting unique values
* Boolean masking
* Broadcasting
* Clipping values with `np.clip()`
* Percentile and quantile analysis
* Matrix multiplication / dot product for weighted scores
* Saving and loading arrays using `np.save()` and `np.load()`

## Analysis Performed

The project answers questions such as:

* What is each student’s total and average score?
* Which student has the highest average score?
* Which student has the lowest average score?
* Which subject has the highest average score?
* Which subject has the lowest average score?
* How many students passed or failed?
* Which students scored below 60 in at least one subject?
* Which individual scores are above 90?
* What happens when subject-wise bonus marks are added?
* How can scores be clipped between 0 and 100?
* What are the 25th, 50th, and 75th percentile scores?
* What are weighted scores when subjects have different importance?

## Output Files

The project saves processed NumPy arrays in the `outputs` folder:

```text
outputs/
├── result.npy
├── weighted_scores.npy
└── student_average_scores.npy
```

## How to Run the Project

From the root folder of the repository, run:

```bash
python pandas-numpy-practice-projects/02-numpy-student-marks-analyzer/marks_analyzer.py
```

## Project Files

```text
02-numpy-student-marks-analyzer/
├── outputs/
│   ├── result.npy
│   ├── weighted_scores.npy
│   └── student_average_scores.npy
├── marks_analyzer.py
├── README.md
└── insights.md
```

## Summary

This project helped me practice the NumPy concepts needed for future machine learning work, especially working with arrays, axes, vectorized calculations, boolean masks, broadcasting, and weighted numerical computations.

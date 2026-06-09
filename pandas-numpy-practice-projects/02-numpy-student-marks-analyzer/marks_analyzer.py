import numpy as np
student_names = ["Nisha", "Riya", "Aman", "Sara", "John", "Meera", "Rahul", "Ananya", "David", "Priya"]
subject_names = ["Math", "Science", "English", "History"]
marks = np.array([
    [85, 88, 90, 78],
    [70, 75, 72, 80],
    [95, 92, 96, 94],
    [60, 58, 65, 70],
    [88, 84, 86, 82],
    [45, 55, 50, 48],
    [78, 81, 79, 85],
    [92, 90, 89, 95],
    [66, 68, 72, 64],
    [98, 96, 94, 99]
])
print(marks)
print(f"The shape of marks array is: {marks.shape}")
print(f"The dimensions of marks array is: {marks.ndim}")
print(f"The size of marks array is: {marks.size}")
print(f"The type of marks array is: {type(marks)}")
print(f"The datatype of marks array is: {marks.dtype}")


students_total_scores = np.sum(marks, axis = 1)
print(f"The student's total scores are: {students_total_scores}")
students_avg_scores = np.mean(marks, axis = 1)
print(f"The student's average scores are: {students_avg_scores}")
student_highest_scores = np.max(marks, axis = 1)
print(f"The student's highest scores are: {student_highest_scores}")
student_lowest_scores = np.min(marks, axis = 1)
print(f"The student's lowest scores are: {student_lowest_scores}")
sub_avg_scores = np.mean(marks, axis = 0)
print(f"The average scores are: {sub_avg_scores}")
sub_highest_scores = np.max(marks, axis = 0)
print(f"The highest scores are: {sub_highest_scores}")
sub_lowest_scores = np.min(marks, axis = 0)
print(f"The lowest scores are: {sub_lowest_scores}")
highest_avg_index = np.argmax(students_avg_scores)
highest_avg_student = student_names[highest_avg_index]
print(f"{highest_avg_student} has the highest average score: {students_avg_scores[highest_avg_index]}")

lowest_avg_index = np.argmin(students_avg_scores)
lowest_avg_student = student_names[lowest_avg_index]
print(f"{lowest_avg_student} has the lowest average score: {students_avg_scores[lowest_avg_index]}")

highest_sub_index = np.argmax(sub_avg_scores)
highest_avg_sub = subject_names[highest_sub_index]
print(f"{highest_avg_sub} has the highest subject average score: {sub_avg_scores[highest_sub_index]}")

lowest_sub_index = np.argmin(sub_avg_scores)
lowest_avg_sub = subject_names[lowest_sub_index]
print(f"{lowest_avg_sub} has the lowest subject average score: {sub_avg_scores[lowest_sub_index]}")

result = np.where(students_avg_scores >=70, "Pass", "Fail")
print(result)
result_count = np.unique(result, return_counts = True)
print(result_count)

for index,value in enumerate(result): 
    if value == "Fail":
        print(f"{student_names[index]} failed")

below_60 = np.any(marks < 60, axis = 1) # For each student, is any subject score below 60
for index,value in enumerate(below_60): 
    if value:
        print(f"{student_names[index]} scored  below 60 in atleast one subject")

above_90 = marks[marks > 90]
print(above_90)

bonus_adjusted = marks + [2,3,2,1]
print(f"Bonus-adjusted marks: {bonus_adjusted}")

clipped_bonus_marks = np.clip(bonus_adjusted,0,100)
print(f"Bonus-adjusted marks clipped: {clipped_bonus_marks}")

percentile_25 = np.percentile(marks, 25)
print(f"The 25th percentile score is {percentile_25}")
percentile_50 = np.percentile(marks, 50)
print(f"The 50th percentile score is {percentile_50}")
percentile_75 = np.percentile(marks, 75)
print(f"The 75th percentile score is {percentile_75}")

quantile_25 = np.quantile(marks, 0.25)
print(f"The 25th quantile score is {quantile_25}")
quantile_50 = np.quantile(marks, 0.50)
print(f"The 50th quantile score is {quantile_50}")
quantile_75 = np.quantile(marks, 0.75)
print(f"The 75th quantile score is {quantile_75}")

weighted_score_arr = []
weightage = np.array([0.30, 0.30, 0.25, 0.15])
for x in range(0,10):
    weighted_score = weightage @ marks[x,:]
    weighted_score_arr.append(weighted_score)
    print(f"The weights score for {student_names[x]} is: {weighted_score:.2f}")

weighted_score_arr = np.array(weighted_score_arr)

highest_weighted_score_index = np.argmax(weighted_score_arr)
highest_weighted_score = weighted_score_arr[highest_weighted_score_index]
print(f"The highest weighted score is {highest_weighted_score:.2f} by {student_names[highest_weighted_score_index]}")

lowest_weighted_score_index = np.argmin(weighted_score_arr)
lowest_weighted_score = weighted_score_arr[lowest_weighted_score_index]
print(f"The lowest weighted score is {lowest_weighted_score:.2f} by {student_names[lowest_weighted_score_index]}")

np.save("pandas-numpy-practice-projects/02-numpy-student-marks-analyzer/outputs/result.npy", result)
np.save("pandas-numpy-practice-projects/02-numpy-student-marks-analyzer/outputs/weighted_scores.npy", weighted_score_arr)
np.save("pandas-numpy-practice-projects/02-numpy-student-marks-analyzer/outputs/student_average_scores.npy", students_avg_scores)

loaded_average_scores = np.load("pandas-numpy-practice-projects/02-numpy-student-marks-analyzer/outputs/student_average_scores.npy")
print(f"Loaded student average scores: {loaded_average_scores}")

















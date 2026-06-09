import pandas as pd

# loading data
df = pd.read_csv("pandas-numpy-practice-projects/01-pandas-student-performance-analysis/data/student_performance_raw.csv")

#Inspecting data
print(f"--------------Data inspection---------------")
print(df.head())
print(df.info())
print(df.describe())
print(df.index)
print(df.columns)

#Check for missing values
print(f"--------------Check for missing values---------------")
print(df.isna())
print(df.isna().sum())

#Fill missing values
print(f"--------------Filling missing values---------------")
df["Science_Score"] = df["Science_Score"].fillna(df["Science_Score"].mean())
df["Age"] = df["Age"].fillna(df["Age"].mean())
df["English_Score"] = df["English_Score"].fillna(df["English_Score"].mean())

#Shape before data cleaning
print(f"Shape before cleaning: {df.shape}")

#Check for duplicates
print(df.duplicated(subset=["Name", "Gender", "Age", "City", "Study_Hours", "Attendance", "Math_Score", "Science_Score", "English_Score", "Internet_Access", "Parent_Education"]))

#Drop duplicates
df = df.drop_duplicates(subset=["Name", "Gender", "Age", "City", "Study_Hours", "Attendance", "Math_Score", "Science_Score", "English_Score", "Internet_Access", "Parent_Education"])

#Shape after data cleaning
print(f"Shape after cleaning: {df.shape}")

#Calculating and add Total_score and average_score columns
df["Total_Score"] = df["Science_Score"] + df["English_Score"] + df["Math_Score"]
df["Average_Score"] = df["Total_Score"]/3

#Deciding whether the student has passed or failed 
df["Result"] = df["Average_Score"].apply(lambda avg: "Pass" if avg >= 70 else "Fail")

#Function to decide student's performance
def performance_level(avg_score):
    match avg_score:
        case avg_score if avg_score >= 90:
            return "Excellent"
        case avg_score if avg_score >= 84:
            return "Good"
        case avg_score if avg_score >= 73:
            return "Average"
        case _:
            return "Needs Improvement"


df["Performance_Level"] = df["Average_Score"].apply(performance_level)

#Function to decide attendance performance
def attendance(presence):
    match presence:
        case presence if presence >= 90:
            return "High Attendance"
        case presence if presence >= 75:
            return "Medium Attendance"
        case _:
            return "Low Attendance"
        
df["Attendance_Category"] = df["Attendance"].apply(attendance)

#Function to decide productivity based on study time
def study(time):
    match time:
        case time if time >= 4:
            return "High Study"
        case time if time >= 2:
            return "Medium Study"
        case _:
            return "Low Study"
        
df["Study_Category"] = df["Study_Hours"].apply(study)

print(df[["Study_Category", "Attendance_Category", "Performance_Level", "Total_Score", "Average_Score", "Result"]])

print(f"--------------Pass/Fail count---------------")
result_count = df.groupby("Result")["Student_ID"].count()
print(result_count)

performance_count = df.groupby("Performance_Level")["Student_ID"].count()
print("--------------Performance Level Count---------------")
print(performance_count)

city_based_avg = df.groupby("City")["Average_Score"].mean()
print("--------------Average Score by City---------------")
print(city_based_avg.round(2))

gender_based_avg = df.groupby("Gender")["Average_Score"].mean()
print("--------------Average Score by Gender---------------")
print(gender_based_avg.round(2))

education_based_avg = df.groupby("Parent_Education")["Average_Score"].mean()
print("--------------Average Score by Parent Education---------------")
print(education_based_avg.round(2))

print("--------------Subject-wise Average Scores---------------")

math_avg = df["Math_Score"].mean()
print(f"The average Math score is: {math_avg:.2f}")

eng_avg = df["English_Score"].mean()
print(f"The average English score is: {eng_avg:.2f}")

science_avg = df["Science_Score"].mean()
print(f"The average Science score is: {science_avg:.2f}")

internet_based_avg = df.groupby("Internet_Access")["Average_Score"].mean()
print("--------------Average Score by Internet Access---------------")
print(internet_based_avg.round(2))

study_based_avg = df.groupby("Study_Category")["Average_Score"].mean()
print("--------------Average Score by Study Category---------------")
print(study_based_avg.round(2))

top5 = df.sort_values("Average_Score", ascending = False)
top5 = top5.head()
print("--------------Top 5 Students by Average Score---------------")
print(top5[["Student_ID", "Name", "Average_Score", "Performance_Level", "Study_Category", "Attendance_Category"]])

at_risk_students = df[(df["Average_Score"] < 70) | (df["Attendance"] < 75)] 
print("--------------Students At Risk---------------")
print(at_risk_students[["Student_ID", "Name", "Average_Score", "Attendance", "Result", "Performance_Level"]])

df["Total_Score"] = df["Science_Score"] + df["English_Score"] + df["Math_Score"]
df["Average_Score"] = df["Total_Score"] / 3

df["Total_Score"] = df["Total_Score"].round(2)
df["Average_Score"] = df["Average_Score"].round(2)
df["Science_Score"] = df["Science_Score"].round(2)
df["English_Score"] = df["English_Score"].round(2)
df["Age"] = df["Age"].round(2)

df.to_csv(
    "pandas-numpy-practice-projects/01-pandas-student-performance-analysis/data/student_performance_cleaned.csv",
    index=False
)

print("Cleaned dataset saved successfully.")
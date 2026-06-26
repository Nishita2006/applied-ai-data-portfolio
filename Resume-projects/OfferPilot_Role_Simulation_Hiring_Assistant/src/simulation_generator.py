def generate_simulation_task(role_category):
    match role_category:
        case "Data / Analytics":
            task = """
You are given a small dataset with columns: date, product, sales, region, and customer_count.

Task:
1. Identify the top-performing region.
2. Find one possible reason sales changed over time.
3. Explain two insights you would share with a manager.
4. Mention one follow-up question you would ask before making a business decision.
"""

        case "AI / ML":
            task = """
You are working on a model that predicts whether a customer will churn.

Task:
1. Choose two evaluation metrics and explain why they matter.
2. Explain why accuracy alone may not be enough.
3. Mention one possible issue with the dataset.
4. Suggest one way to improve the model.
"""

        case "Software Engineering":
            task = """
A web app is loading slowly after users submit a form.

Task:
1. Explain how you would debug the issue.
2. Mention what parts of the app you would check first.
3. Suggest one backend improvement.
4. Suggest one way to prevent similar issues in the future.
"""

        case "Finance / Risk":
            task = """
A bank notices an increase in suspicious transactions.

Task:
1. Identify three signals that could indicate fraud.
2. Explain how you would prioritize which transactions to review.
3. Mention one risk of false positives.
4. Suggest one dashboard metric for monitoring fraud trends.
"""

        case "HR / People Operations":
            task = """
A company is hiring interns and wants to improve its recruiting process.

Task:
1. Identify two issues that could slow down hiring.
2. Suggest one way to improve candidate communication.
3. Explain how you would track recruiting progress.
4. Mention one metric HR should monitor.
"""

        case "Product / Business":
            task = """
A product team is deciding whether to launch a new feature.

Task:
1. Choose three metrics to evaluate the feature.
2. Explain which metric matters most and why.
3. Mention one user risk or business risk.
4. Suggest one experiment before full launch.
"""

        case _:
            task = """
Review the role and candidate background.

Task:
1. Identify the most important skills for this role.
2. Explain how you would evaluate a candidate's fit.
3. Mention one possible concern to verify.
4. Suggest one interview question for this candidate.
"""

    return task.strip()
def score_simulation_response(candidate_answer, role_category):
    answer = candidate_answer.lower()

    technical_score = 1
    reasoning_score = 1
    relevance_score = 1
    communication_score = 1
    tradeoff_score = 1

    # Role-specific keywords for technical scoring
    match role_category:
        case "Data / Analytics":
            technical_keywords = [
                "data", "insight", "trend", "metric",
                "analysis", "sales", "region"
            ]

        case "AI / ML":
            technical_keywords = [
                "model", "accuracy", "precision", "recall",
                "dataset", "feature", "metric"
            ]

        case "Software Engineering":
            technical_keywords = [
                "debug", "backend", "frontend", "api",
                "database", "server", "performance"
            ]

        case "Finance / Risk":
            technical_keywords = [
                "fraud", "risk", "transaction", "false positive",
                "monitor", "suspicious"
            ]

        case "HR / People Operations":
            technical_keywords = [
                "recruiting", "candidate", "communication",
                "hiring", "onboarding", "metric"
            ]

        case "Product / Business":
            technical_keywords = [
                "user", "feature", "metric", "experiment",
                "launch", "business", "risk"
            ]

        case _:
            technical_keywords = [
                "skill", "candidate", "role", "experience", "question"
            ]

    keyword_matches = 0

    for keyword in technical_keywords:
        if keyword in answer:
            keyword_matches += 1

    if keyword_matches >= 5:
        technical_score = 5
    elif keyword_matches >= 4:
        technical_score = 4
    elif keyword_matches >= 3:
        technical_score = 3
    elif keyword_matches >= 2:
        technical_score = 2

    # Reasoning score checks for explanation words
    reasoning_words = [
        "because", "so that", "therefore",
        "this means", "i would", "first", "then"
    ]

    reasoning_matches = 0

    for word in reasoning_words:
        if word in answer:
            reasoning_matches += 1

    if reasoning_matches >= 4:
        reasoning_score = 5
    elif reasoning_matches == 3:
        reasoning_score = 4
    elif reasoning_matches == 2:
        reasoning_score = 3
    elif reasoning_matches == 1:
        reasoning_score = 2

    # Relevance score uses answer length as a simple signal
    word_count = len(answer.split())

    if word_count >= 150:
        relevance_score = 5
    elif word_count >= 100:
        relevance_score = 4
    elif word_count >= 60:
        relevance_score = 3
    elif word_count >= 30:
        relevance_score = 2

    # Communication score checks basic structure
    if "\n" in candidate_answer and word_count >= 80:
        communication_score = 5
    elif word_count >= 80:
        communication_score = 4
    elif word_count >= 50:
        communication_score = 3
    elif word_count >= 25:
        communication_score = 2

    # Tradeoff score checks risk/limitation language
    tradeoff_words = [
        "risk", "tradeoff", "assumption", "however", "but",
        "limitation", "false positive", "false negative"
    ]

    tradeoff_matches = 0

    for word in tradeoff_words:
        if word in answer:
            tradeoff_matches += 1

    if tradeoff_matches >= 3:
        tradeoff_score = 5
    elif tradeoff_matches == 2:
        tradeoff_score = 4
    elif tradeoff_matches == 1:
        tradeoff_score = 3

    total_score = (
        technical_score
        + reasoning_score
        + relevance_score
        + communication_score
        + tradeoff_score
    )

    simulation_score = round((total_score / 25) * 100, 2)

    return {
        "Technical Correctness": technical_score,
        "Reasoning Clarity": reasoning_score,
        "Role Relevance": relevance_score,
        "Communication": communication_score,
        "Assumptions / Tradeoffs": tradeoff_score,
        "Simulation Score": simulation_score
    }
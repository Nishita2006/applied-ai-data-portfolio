import unittest

from src.interview_analyzer import analyze_interview_transcript
from src.semantic_matcher import build_contextual_match_report, match_skill_to_resume


class ContextualMatcherTests(unittest.TestCase):
    def test_synonym_match(self):
        result = match_skill_to_resume(
            "machine learning",
            "Built predictive modeling pipelines and evaluated model performance.",
        )
        self.assertEqual(result["status"], "Matched")
        self.assertEqual(result["match_type"], "Synonym")

    def test_negated_skill_is_not_matched(self):
        result = match_skill_to_resume(
            "docker",
            "I have no experience with Docker but would like to learn it.",
        )
        self.assertEqual(result["status"], "Missing evidence")

    def test_report_separates_missing_evidence(self):
        report = build_contextual_match_report(
            ["python", "docker"],
            "Implemented a Python data pipeline for a university project.",
        )
        self.assertIn("python", report["matched"])
        self.assertIn("docker", report["missing"])
        self.assertEqual(report["score"], 50)

    def test_contextual_data_analysis_gets_partial_credit(self):
        result = match_skill_to_resume(
            "data analysis",
            "Evaluated detection performance by measuring accuracy and false positives.",
        )
        self.assertEqual(result["status"], "Partial")
        self.assertEqual(result["match_type"], "Contextual evidence")

    def test_api_variants_are_one_competency(self):
        report = build_contextual_match_report(
            ["api", "apis"],
            "Architected RESTful APIs for authentication and request routing.",
        )
        self.assertEqual(len(report["matches"]), 1)
        self.assertEqual(report["matched"], ["api"])


class InterviewAnalyzerTests(unittest.TestCase):
    def test_concrete_answer_scores_above_vague_answer(self):
        concrete = analyze_interview_transcript(
            "I built the Python API because batch processing was too slow. "
            "I tested it on 500 records, debugged a timeout, and reduced latency 30%.",
            role_skills=["python", "api"],
        )
        vague = analyze_interview_transcript(
            "We did various tasks and I helped with best practices on the project.",
            role_skills=["python", "api"],
        )
        self.assertGreater(concrete["evidence_score"], vague["evidence_score"])
        self.assertIn("python", concrete["supported_skills"])


if __name__ == "__main__":
    unittest.main()

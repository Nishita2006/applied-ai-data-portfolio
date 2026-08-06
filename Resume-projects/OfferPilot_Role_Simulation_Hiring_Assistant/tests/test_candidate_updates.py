import unittest

from src.candidate_updates import (
    MILESTONES,
    build_status_message,
    extract_phone_number,
    milestone_progress,
    validate_phone_number,
)


class CandidateUpdateTests(unittest.TestCase):
    def test_phone_number_requires_e164(self):
        self.assertTrue(validate_phone_number("+15551234567"))
        self.assertFalse(validate_phone_number("555-123-4567"))
        self.assertFalse(validate_phone_number("+01234567"))

    def test_extracts_international_and_configured_national_numbers(self):
        self.assertEqual(extract_phone_number("Phone: +1 (608) 690-0370"), "+16086900370")
        self.assertEqual(
            extract_phone_number("Phone: 608-690-0370", "+1"),
            "+16086900370",
        )

    def test_progress_counts_completed_and_in_progress(self):
        statuses = {key: "Not started" for key, _ in MILESTONES}
        statuses["application_received"] = "Completed"
        statuses["resume_review"] = "In progress"
        self.assertAlmostEqual(milestone_progress(statuses), 1.5 / len(MILESTONES))

    def test_message_is_candidate_facing(self):
        message = build_status_message(
            "Maya Patel",
            "Interview",
            "In progress",
            "Choose an interview time.",
        )
        self.assertIn("Maya", message)
        self.assertIn("Interview", message)
        self.assertIn("Choose an interview time", message)


if __name__ == "__main__":
    unittest.main()

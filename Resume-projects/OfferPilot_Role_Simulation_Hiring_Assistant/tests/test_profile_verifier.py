import unittest

from src.profile_verifier import compare_resume_with_profiles, extract_profile_links


class ProfileVerifierTests(unittest.TestCase):
    def test_extracts_github_and_linkedin_profiles(self):
        links = extract_profile_links(
            "GitHub: https://github.com/example-user "
            "LinkedIn: https://www.linkedin.com/in/example.profile"
        )
        self.assertEqual(links["github_username"], "example-user")
        self.assertEqual(links["linkedin_url"], "https://www.linkedin.com/in/example.profile")

    def test_profile_overlap_uses_public_project_evidence(self):
        result = compare_resume_with_profiles(
            "Built a Python FastAPI inventory application.",
            {
                "bio": "Python developer",
                "repos": [
                    {
                        "name": "inventory-api",
                        "description": "FastAPI inventory application",
                        "language": "Python",
                    }
                ],
            },
        )
        self.assertIn("python", result["github_shared_terms"])
        self.assertGreater(result["github_overlap"], 0)


if __name__ == "__main__":
    unittest.main()

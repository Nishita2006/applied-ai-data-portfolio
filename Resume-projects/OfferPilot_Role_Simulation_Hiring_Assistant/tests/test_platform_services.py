import tempfile
import unittest
from pathlib import Path

import src.platform_services as platform


class PlatformServicesTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_path = platform.DB_PATH
        platform.DB_PATH = Path(self.temp_dir.name) / "test.db"
        platform.init_platform_db()

    def tearDown(self):
        platform.DB_PATH = self.original_path
        self.temp_dir.cleanup()

    def test_user_authentication_and_roles(self):
        platform.create_user("admin@example.com", "Admin", "admin", "strong-pass-123")
        user = platform.authenticate_user("admin@example.com", "strong-pass-123")
        self.assertEqual(user["role"], "admin")
        self.assertIsNone(platform.authenticate_user("admin@example.com", "wrong-password"))

    def test_persistence_audit_and_portal_token(self):
        job_id = platform.save_job("Engineer", "Build systems", {"required_skills": ["python"]}, "admin")
        candidate_id = platform.save_candidate(
            job_id,
            "Candidate One",
            "Python experience",
            {"ats": {"score": 80}},
            actor="admin",
        )
        platform.save_candidate(
            job_id,
            "Candidate One",
            "Python experience",
            {"decision": "Move Forward"},
            actor="admin",
        )
        saved = platform.list_candidates(job_id)[0]
        self.assertIn('"ats"', saved["workflow_json"])
        self.assertIn('"decision"', saved["workflow_json"])
        token = platform.create_portal_token(candidate_id)
        self.assertEqual(platform.resolve_portal_token(token)["name"], "Candidate One")
        self.assertGreaterEqual(len(platform.list_audit_events()), 3)


if __name__ == "__main__":
    unittest.main()

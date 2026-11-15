import unittest

from emnlp_audit import paths
from emnlp_audit.files import read_csv
from emnlp_audit.policy.sources import html_to_text, sha256


class HtmlToTextTest(unittest.TestCase):
    def test_strips_markup_scripts_and_empty_bullets(self):
        raw = b"<html><script>var x=1;</script><ul><li></li><li>Limitations</li></ul><p>A &amp; B</p></html>"
        text = html_to_text(raw)
        self.assertIn("- Limitations", text)
        self.assertIn("A & B", text)
        self.assertNotIn("var x", text)
        self.assertNotIn("\n-\n", text)


class CommittedSnapshotsTest(unittest.TestCase):
    def test_committed_snapshots_match_recorded_checksums(self):
        for row in read_csv(paths.POLICY_DOCUMENTS_PATH):
            if not row["local_path"]:
                self.assertTrue(row["notes"].startswith("NO SNAPSHOT"), row["doc_id"])
                continue
            data = paths.from_repo_relative(row["local_path"]).read_bytes()
            self.assertEqual(sha256(data), row["sha256"], row["doc_id"])


if __name__ == "__main__":
    unittest.main()

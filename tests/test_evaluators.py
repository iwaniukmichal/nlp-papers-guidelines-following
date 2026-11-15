import unittest

from emnlp_audit.analysis.iaa import cohens_kappa
from emnlp_audit.analysis.validation import macro_f1
from emnlp_audit.evaluators.llm import verify_quote_in_text
from emnlp_audit.parsing.checklist_strip import join_pages_without_checklist
from emnlp_audit.parsing.pii import redact_emails


class QuoteVerificationTest(unittest.TestCase):
    TEXT = "--- [PAGE 8] ---\nLimitations\nThe model assumes accurate tran-\nscripts; recognition errors may reduce accuracy."

    def test_empty_quote_is_trivially_verified(self):
        self.assertTrue(verify_quote_in_text("", self.TEXT))

    def test_tolerates_line_break_hyphenation(self):
        self.assertTrue(verify_quote_in_text("The model assumes accurate transcripts; recognition errors", self.TEXT))

    def test_rejects_fabricated_quote(self):
        self.assertFalse(verify_quote_in_text("We trained on 512 TPUs for three months.", self.TEXT))


class ParsingTest(unittest.TestCase):
    def test_checklist_and_following_pages_are_removed(self):
        pages = [
            {"page": 1, "text": "Main text"},
            {"page": 2, "text": "Refs\nResponsible NLP Research Checklist\nA1 yes"},
            {"page": 3, "text": "B1 yes"},
        ]
        text, cut = join_pages_without_checklist(pages)
        self.assertEqual(cut, 2)
        self.assertIn("Main text", text)
        self.assertIn("Refs", text)
        self.assertNotIn("A1 yes", text)
        self.assertNotIn("B1 yes", text)

    def test_emails_redacted(self):
        self.assertEqual(redact_emails("contact: a.b@uni.edu"), "contact: [EMAIL_REDACTED]")


class MetricsTest(unittest.TestCase):
    def test_kappa_perfect_and_chance(self):
        self.assertEqual(cohens_kappa(["a", "b", "a"], ["a", "b", "a"]), 1.0)
        self.assertEqual(cohens_kappa(["a", "a", "b", "b"], ["a", "b", "a", "b"]), 0.0)

    def test_macro_f1_ignores_classes_without_support(self):
        result = macro_f1(["a", "a"], ["a", "b"])
        self.assertEqual(result["per_class"]["b"]["support"], 0)
        self.assertAlmostEqual(result["macro_f1"], round(2 * 1.0 * 0.5 / 1.5, 4))


if __name__ == "__main__":
    unittest.main()

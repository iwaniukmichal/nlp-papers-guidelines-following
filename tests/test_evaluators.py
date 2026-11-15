import unittest

from emnlp_audit.analysis.iaa import cohens_kappa
from emnlp_audit.analysis.validation import macro_f1
from emnlp_audit.evaluators.llm import MAX_PAPER_CHARS, to_records, verify_quote_in_text
from emnlp_audit.parsing.checklist_strip import join_pages_without_checklist
from emnlp_audit.parsing.pii import redact_emails


class QuoteVerificationTest(unittest.TestCase):
    TEXT = (
        "--- [PAGE 8] ---\nLimitations\n"
        "The model assumes accurate tran-\nscripts; recognition errors may reduce accuracy. "
        "Furthermore, our Speciﬁc evaluation only covers English datasets."
    )

    def test_empty_quote_is_trivially_verified(self):
        self.assertTrue(verify_quote_in_text("", self.TEXT))

    def test_tolerates_line_break_hyphenation_and_ligatures(self):
        self.assertTrue(
            verify_quote_in_text(
                "The model assumes accurate transcripts; recognition errors may reduce accuracy. "
                "Furthermore, our Specific evaluation only covers English datasets.",
                self.TEXT,
            )
        )

    def test_supports_ordered_ellipsis_segments(self):
        self.assertTrue(
            verify_quote_in_text(
                "The model assumes accurate transcripts ... our Specific evaluation only covers English datasets.",
                self.TEXT,
            )
        )

    def test_rejects_quote_with_fabricated_ending(self):
        self.assertFalse(
            verify_quote_in_text(
                "The model assumes accurate transcripts; recognition errors may reduce accuracy "
                "and we trained on 512 TPUs for three months.",
                self.TEXT,
            )
        )

    def test_rejects_fabricated_quote(self):
        self.assertFalse(verify_quote_in_text("We trained on 512 TPUs for three months.", self.TEXT))

    def test_truncation_and_unverified_quote_marked_uncertain(self):
        paper = {"anthology_id": "2024.emnlp-main.1", "year": 2024, "track": "Main"}
        rubric = {
            "items": [
                {"item_id": "I1_limitations_section", "policy_mandate_years": [2024]},
                {"item_id": "I4_computational_budget", "policy_mandate_years": [2024]},
            ]
        }
        response = {
            "evaluations": [
                {
                    "item_id": "I1_limitations_section",
                    "practice_applies": True,
                    "evidence_status": "adequately_reported",
                    "evidence_quote": "Fabricated quote not in text",
                    "location": "Page 9",
                    "justification": "Found section.",
                },
                {
                    "item_id": "I4_computational_budget",
                    "practice_applies": True,
                    "evidence_status": "not_reported",
                    "evidence_quote": "",
                    "location": "",
                    "justification": "Not mentioned.",
                },
            ]
        }
        long_text = self.TEXT + (" " + "appendix text" * 10_000)
        self.assertGreater(len(long_text), MAX_PAPER_CHARS)
        records = to_records(paper, response, long_text, rubric, "gemini-2.5-flash")
        by_id = {r["item_id"]: r for r in records}

        # Unverified quote -> uncertain
        self.assertFalse(by_id["I1_limitations_section"]["quote_verified_in_text"])
        self.assertEqual(by_id["I1_limitations_section"]["evidence_status"], "uncertain")
        self.assertEqual(by_id["I1_limitations_section"]["derived_compliance"], "Uncertain")

        # Truncated paper + not_reported -> uncertain
        self.assertTrue(by_id["I4_computational_budget"]["text_truncated"])
        self.assertEqual(by_id["I4_computational_budget"]["evidence_status"], "uncertain")
        self.assertEqual(by_id["I4_computational_budget"]["derived_compliance"], "Uncertain")


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

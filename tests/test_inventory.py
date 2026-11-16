import unittest

from emnlp_audit.policy import inventory as inv


def row(**overrides):
    base = {
        "req_id": "LIMITATIONS_SECTION", "year": "2022", "doc_id": "EMNLP2022-CFP",
        "quote": "Papers without a limitation section will be automatically rejected without review.",
        "location": "", "where_reported": "paper", "status": "mandatory_in_paper", "condition": "",
        "route": "all", "tracks": "all_submissions", "coded_by": "a", "verified_by": "", "verification": "pending",
        "notes": "",
    }
    base.update(overrides)
    return base


class ValidateTest(unittest.TestCase):
    DICT = {"LIMITATIONS_SECTION": {}}

    def errors(self, rows):
        # ignore coverage errors: these tests use single rows
        return [e for e in inv.validate(rows, self.DICT) if not e.startswith("coverage")]

    def test_real_quote_passes(self):
        self.assertEqual(self.errors([row()]), [])

    def test_fabricated_quote_is_rejected(self):
        errs = self.errors([row(quote="Papers without a limitation section will receive a warning.")])
        self.assertTrue(any("not found verbatim" in e for e in errs))

    def test_curly_quotes_and_whitespace_are_normalized(self):
        q = 'EMNLP 2022 requires all papers to have a clear discussion of limitations, in a dedicated   section titled "Limitations".'
        self.assertEqual(self.errors([row(quote=q)]), [])

    def test_verifier_must_differ_from_coder(self):
        errs = self.errors([row(verification="verified", verified_by="a")])
        self.assertTrue(any("verifier" in e for e in errs))

    def test_unverified_needs_reason(self):
        errs = self.errors([row(status="unverified", quote="", notes="")])
        self.assertTrue(any("explain" in e for e in errs))


class YearLevelTest(unittest.TestCase):
    def test_strongest_status_per_route(self):
        rows = [
            row(status="reviewer_criterion", route="direct", quote=""),
            row(status="checklist_question", route="arr", quote=""),
            row(status="recommended", route="all", quote=""),
        ]
        result = {r["route"]: r["status"] for r in inv.year_level(rows)}
        self.assertEqual(result, {"direct": "reviewer_criterion", "arr": "checklist_question"})

    def test_known_status_beats_unverified(self):
        rows = [row(status="unverified", quote=""), row(status="recommended", quote="")]
        self.assertEqual(inv.year_level(rows)[0]["status"], "recommended")


class CommittedInventoryTest(unittest.TestCase):
    def test_committed_inventory_is_valid(self):
        self.assertEqual(inv.validate(inv.load_inventory(), inv.load_dictionary()), [])

    def test_committed_dictionary_is_valid(self):
        self.assertEqual(inv.validate_dictionary(inv.load_dictionary()), [])


if __name__ == "__main__":
    unittest.main()

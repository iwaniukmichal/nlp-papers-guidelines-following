import unittest

from emnlp_audit.evaluators.compliance import derive_compliance, policy_applies


class DeriveComplianceTest(unittest.TestCase):
    def test_compliant_when_policy_and_practice_apply_and_adequate(self):
        self.assertEqual(derive_compliance(True, True, "adequately_reported"), "Compliant")

    def test_non_compliant_for_missing_or_inadequate_evidence(self):
        self.assertEqual(derive_compliance(True, True, "not_reported"), "Non-compliant")
        self.assertEqual(derive_compliance(True, True, "explicitly_reported_inadequate"), "Non-compliant")

    def test_not_applicable_without_policy_or_practice(self):
        self.assertEqual(derive_compliance(False, True, "not_reported"), "Not applicable")
        self.assertEqual(derive_compliance(True, False, "not_reported"), "Not applicable")
        self.assertEqual(derive_compliance(True, True, "not_applicable"), "Not applicable")

    def test_uncertain_takes_precedence(self):
        self.assertEqual(derive_compliance(False, "uncertain", "adequately_reported"), "Uncertain")
        self.assertEqual(derive_compliance(True, True, "uncertain"), "Uncertain")
        self.assertEqual(derive_compliance("unverified", True, "adequately_reported"), "Uncertain")
        self.assertEqual(derive_compliance(True, True, "something_unexpected"), "Uncertain")


class PolicyAppliesTest(unittest.TestCase):
    def test_uses_mandate_years_fallback(self):
        item = {"policy_mandate_years": [2022, 2023]}
        self.assertTrue(policy_applies(item, 2022))
        self.assertTrue(policy_applies(item, "2023"))
        self.assertFalse(policy_applies(item, 2021))

    def test_reads_requirements_csv_and_routes(self):
        self.assertFalse(policy_applies("I1_limitations_section", 2021))
        self.assertTrue(policy_applies("I1_limitations_section", 2022, route="direct"))
        self.assertTrue(policy_applies("I1_limitations_section", 2022, route="arr"))
        self.assertTrue(policy_applies("I1_limitations_section", 2022, route="all"))
        self.assertTrue(policy_applies("I3_ethical_risks", 2020))
        self.assertFalse(policy_applies("I4_computational_budget", 2024))
        self.assertFalse(policy_applies("I5_asset_licensing", 2024))
        self.assertFalse(policy_applies("I6_ai_assistance", 2025))


if __name__ == "__main__":
    unittest.main()

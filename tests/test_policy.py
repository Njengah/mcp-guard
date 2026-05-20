import unittest

from mcpguard.policy import evaluate_policy, validate_mode
from mcpguard.errors import InvalidPolicyModeError


class PolicyTests(unittest.TestCase):
    def test_evaluate_explicit_modes(self):
        self.assertEqual(evaluate_policy("block").decision, "BLOCK")
        self.assertEqual(evaluate_policy("approve").decision, "REQUIRE_APPROVAL")
        self.assertEqual(evaluate_policy("allow").decision, "ALLOW")

    def test_missing_policy_requires_approval(self):
        decision = evaluate_policy(None)
        self.assertEqual(decision.decision, "REQUIRE_APPROVAL")
        self.assertIn("No explicit policy", decision.reason)

    def test_validate_mode(self):
        self.assertEqual(validate_mode("ALLOW"), "allow")
        with self.assertRaises(InvalidPolicyModeError):
            validate_mode("deny")


if __name__ == "__main__":
    unittest.main()


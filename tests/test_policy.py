import unittest

from mcpguard.errors import InvalidPolicyModeError
from mcpguard.policy import evaluate_policy, validate_mode
from mcpguard.risk import high_risk_threshold, risk_score


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

    def test_default_risk_score_preserves_existing_behavior(self):
        self.assertEqual(risk_score("read_file", "allow"), 30)
        self.assertEqual(risk_score("delete_repo", "block"), 90)
        self.assertEqual(risk_score("delete_repo", None), 80)

    def test_custom_risk_keywords_and_modifiers(self):
        config = {
            "risk": {
                "base_score": 20,
                "keywords": ["archive"],
                "keyword_modifier": 25,
                "mode_modifiers": {
                    "allow": -5,
                    "approve": 15,
                    "block": 35,
                    "unknown": 12,
                },
            }
        }
        self.assertEqual(risk_score("archive_project", "approve", config), 60)
        self.assertEqual(risk_score("read_file", "allow", config), 15)

    def test_server_and_pack_modifiers(self):
        config = {
            "risk": {
                "server_defaults": {"database": 15},
                "pack_defaults": {"github": 10},
            }
        }
        self.assertEqual(risk_score("read_query", "allow", config, server="database"), 45)
        self.assertEqual(risk_score("read_file", "allow", config, policy_pack="github"), 40)

    def test_custom_high_risk_threshold(self):
        self.assertEqual(high_risk_threshold({"risk": {"high_risk_threshold": 65}}), 65)


if __name__ == "__main__":
    unittest.main()

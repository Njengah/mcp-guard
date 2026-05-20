import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def run_cli(self, cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT / "src")
        return subprocess.run(
            [sys.executable, "-m", "mcpguard", *args],
            cwd=cwd,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_smoke_workflow(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            cwd = Path(temp_dir)

            result = self.run_cli(cwd, "init")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((cwd / ".mcpguard" / "config.json").exists())

            result = self.run_cli(cwd, "add-server", "github")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Added server", result.stdout)

            result = self.run_cli(cwd, "policy", "add", "github", "delete_repo", "--mode", "block")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Policy saved", result.stdout)

            result = self.run_cli(cwd, "inspect")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("[BLOCK] delete_repo: block", result.stdout)

            result = self.run_cli(cwd, "simulate", "github", "delete_repo")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Decision: BLOCK", result.stdout)

            result = self.run_cli(cwd, "report")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((cwd / ".mcpguard" / "reports" / "report.md").exists())

    def test_missing_init_errors(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.run_cli(Path(temp_dir), "inspect")
            self.assertEqual(result.returncode, 1)
            self.assertIn("Run 'mcpguard init' first", result.stderr)

    def test_unknown_server_errors(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            cwd = Path(temp_dir)
            self.assertEqual(self.run_cli(cwd, "init").returncode, 0)
            result = self.run_cli(cwd, "simulate", "missing", "tool")
            self.assertEqual(result.returncode, 1)
            self.assertIn("Unknown server", result.stderr)

    def test_invalid_policy_mode_errors(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            cwd = Path(temp_dir)
            self.assertEqual(self.run_cli(cwd, "init").returncode, 0)
            self.assertEqual(self.run_cli(cwd, "add-server", "github").returncode, 0)
            result = self.run_cli(cwd, "policy", "add", "github", "tool", "--mode", "deny")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("invalid choice", result.stderr)


if __name__ == "__main__":
    unittest.main()


import json
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

    def test_policy_export_writes_json_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            cwd = Path(temp_dir)
            export_path = cwd / "policies-export.json"

            self.assertEqual(self.run_cli(cwd, "init").returncode, 0)
            self.assertEqual(self.run_cli(cwd, "add-server", "github").returncode, 0)
            self.assertEqual(
                self.run_cli(cwd, "policy", "add", "github", "delete_repo", "--mode", "block").returncode,
                0,
            )

            result = self.run_cli(cwd, "policy", "export", str(export_path))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Policies exported", result.stdout)

            exported = json.loads(export_path.read_text(encoding="utf-8"))
            self.assertEqual(exported["schema_version"], "0.1")
            self.assertEqual(exported["servers"]["github"]["delete_repo"]["mode"], "block")

    def test_policy_export_prints_json_without_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            cwd = Path(temp_dir)
            self.assertEqual(self.run_cli(cwd, "init").returncode, 0)

            result = self.run_cli(cwd, "policy", "export")
            self.assertEqual(result.returncode, 0, result.stderr)
            exported = json.loads(result.stdout)
            self.assertEqual(exported["schema_version"], "0.1")
            self.assertEqual(exported["servers"], {})

    def test_policy_import_replaces_local_policies(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            cwd = Path(temp_dir)
            import_path = cwd / "policies-import.json"
            imported = {
                "schema_version": "0.1",
                "created_at": "2026-05-20T00:00:00+00:00",
                "servers": {
                    "github": {
                        "read_file": {
                            "server": "github",
                            "tool": "read_file",
                            "mode": "ALLOW",
                        }
                    }
                },
            }
            import_path.write_text(json.dumps(imported), encoding="utf-8")

            self.assertEqual(self.run_cli(cwd, "init").returncode, 0)
            self.assertEqual(self.run_cli(cwd, "add-server", "github").returncode, 0)
            self.assertEqual(
                self.run_cli(cwd, "policy", "add", "github", "delete_repo", "--mode", "block").returncode,
                0,
            )

            result = self.run_cli(cwd, "policy", "import", str(import_path))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Policies imported: 1", result.stdout)

            policies = json.loads((cwd / ".mcpguard" / "policies.json").read_text(encoding="utf-8"))
            self.assertEqual(policies["servers"]["github"]["read_file"]["mode"], "allow")
            self.assertNotIn("delete_repo", policies["servers"]["github"])

    def test_policy_import_rejects_invalid_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            cwd = Path(temp_dir)
            import_path = cwd / "bad.json"
            import_path.write_text("{bad", encoding="utf-8")

            self.assertEqual(self.run_cli(cwd, "init").returncode, 0)
            result = self.run_cli(cwd, "policy", "import", str(import_path))
            self.assertEqual(result.returncode, 1)
            self.assertIn("Corrupted JSON file", result.stderr)

    def test_policy_import_rejects_unknown_schema(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            cwd = Path(temp_dir)
            import_path = cwd / "unknown-schema.json"
            import_path.write_text(
                json.dumps({"schema_version": "9.9", "servers": {}}),
                encoding="utf-8",
            )

            self.assertEqual(self.run_cli(cwd, "init").returncode, 0)
            result = self.run_cli(cwd, "policy", "import", str(import_path))
            self.assertEqual(result.returncode, 1)
            self.assertIn("Unsupported policy schema version", result.stderr)

    def test_policy_import_rejects_invalid_policy_shape(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            cwd = Path(temp_dir)
            import_path = cwd / "bad-shape.json"
            import_path.write_text(
                json.dumps({"schema_version": "0.1", "servers": {"github": []}}),
                encoding="utf-8",
            )

            self.assertEqual(self.run_cli(cwd, "init").returncode, 0)
            result = self.run_cli(cwd, "policy", "import", str(import_path))
            self.assertEqual(result.returncode, 1)
            self.assertIn("Policies for server 'github' must be an object", result.stderr)


if __name__ == "__main__":
    unittest.main()

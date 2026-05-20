import tempfile
import unittest
from pathlib import Path

from mcpguard.errors import CorruptedStateError
from mcpguard.storage import init_state, project_paths, read_json, write_json


class StorageTests(unittest.TestCase):
    def test_init_state_creates_expected_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = project_paths(Path(temp_dir))
            init_state(paths)

            self.assertTrue(paths.config_file.exists())
            self.assertTrue(paths.policies_file.exists())
            self.assertTrue(paths.logs_dir.exists())
            self.assertTrue(paths.reports_dir.exists())

    def test_write_and_read_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "state.json"
            write_json(path, {"ok": True})
            self.assertEqual(read_json(path), {"ok": True})

    def test_corrupted_json_raises_clear_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "bad.json"
            path.write_text("{bad", encoding="utf-8")
            with self.assertRaises(CorruptedStateError):
                read_json(path)


if __name__ == "__main__":
    unittest.main()


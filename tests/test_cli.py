import asyncio
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class CLISubcommandTests(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.tmp_dir.name)
        self.src_dir = self.test_dir / "src"
        self.src_dir.mkdir()

        # Create a sample python file with Doc comments
        sample_file = self.src_dir / "math_utils.py"
        sample_file.write_text(
            '# Doc code : Add numbers\n'
            '# Adds two integers together.\n'
            'def add(a: int, b: int) -> int:\n'
            '    return a + b\n'
            '# Doc end\n',
            encoding="utf-8",
        )

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_cli_help(self):
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "main.py"), "--help"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("build", result.stdout)
        self.assertIn("serve", result.stdout)
        self.assertIn("preview", result.stdout)
        self.assertIn("init", result.stdout)

    def test_cli_build(self):
        out_file = self.test_dir / "out"
        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "main.py"),
                "build",
                str(self.src_dir),
                "-o",
                str(out_file),
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        generated_md = self.test_dir / "out.md"
        self.assertTrue(generated_md.is_file())
        content = generated_md.read_text(encoding="utf-8")
        self.assertIn("Add numbers", content)
        self.assertIn("Adds two integers together", content)
        self.assertIn("def add", content)

    def test_cli_init(self):
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "main.py"), "init"],
            cwd=str(self.test_dir),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        config_file = self.test_dir / "codedocplus.json"
        self.assertTrue(config_file.is_file())
        with open(config_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("title", data)


if __name__ == "__main__":
    unittest.main()

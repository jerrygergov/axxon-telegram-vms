import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
LEGACY_PYTHON = Path("/opt/miniconda3/bin/python3")


class RuntimeCompatibilityTests(unittest.TestCase):
    def test_local_scripts_package_wins_module_resolution(self):
        spec = importlib.util.find_spec("scripts")
        self.assertIsNotNone(spec)
        origin = str((spec.origin or "")).replace("\\", "/")
        expected = str((SCRIPTS_DIR / "__init__.py").resolve()).replace("\\", "/")
        self.assertEqual(origin, expected)

    def test_active_script_modules_import_under_current_python(self):
        proc = subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    "import sys; "
                    f"sys.path.insert(0, {str(ROOT)!r}); "
                    "import scripts.tg_ui_common; "
                    "import scripts.camera_catalog; "
                    "import scripts.media_utils"
                ),
            ],
            text=True,
            capture_output=True,
            cwd=ROOT,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)

    def test_active_script_modules_import_under_python39_if_available(self):
        if not LEGACY_PYTHON.exists():
            self.skipTest("Python 3.9 interpreter not available")

        proc = subprocess.run(
            [
                str(LEGACY_PYTHON),
                "-c",
                (
                    "import sys; "
                    f"sys.path.insert(0, {str(ROOT)!r}); "
                    "import scripts.tg_ui_common; "
                    "import scripts.camera_catalog; "
                    "import scripts.media_utils"
                ),
            ],
            text=True,
            capture_output=True,
            cwd=ROOT,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)


if __name__ == "__main__":
    unittest.main()

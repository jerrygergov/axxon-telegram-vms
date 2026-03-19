import os
import stat
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN_SCRIPT = ROOT / "scripts" / "run_axxon_tg_bot.sh"


def _write_python_stub(path: Path, version: str):
    supported = version.startswith("3.11.") or version.startswith("3.12.") or version.startswith("3.13.")
    script = textwrap.dedent(
        f"""\
        #!/bin/sh
        if [ "$1" = "-V" ] || [ "$1" = "--version" ]; then
          echo "Python {version}"
          exit 0
        fi
        if [ "$1" = "-c" ]; then
          {"exit 0" if supported else "exit 1"}
        fi
        echo "stub:{path.name}:$@" >&2
        exit 0
        """
    )
    path.write_text(script, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


class RuntimeEnvironmentTests(unittest.TestCase):
    def test_readme_declares_python_3_11_or_newer(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("Python 3.11+", readme)

    def test_run_script_prefers_supported_fallback_interpreter_in_dry_run(self):
        with tempfile.TemporaryDirectory() as td:
            bindir = Path(td)
            _write_python_stub(bindir / "python3", "3.9.12")
            _write_python_stub(bindir / "python3.11", "3.11.9")
            env = os.environ.copy()
            env.update(
                {
                    "PATH": f"{bindir}:/bin:/usr/bin",
                    "AXXON_TG_DRY_RUN": "1",
                    "TG_BOT_TOKEN": "token",
                    "AXXON_HOST": "example.local",
                    "AXXON_PASS": "secret",
                }
            )
            result = subprocess.run(
                [str(RUN_SCRIPT)],
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
            )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("PYTHON_BIN=python3.11", result.stdout)

    def test_run_script_fails_cleanly_when_only_old_python_exists(self):
        with tempfile.TemporaryDirectory() as td:
            bindir = Path(td)
            _write_python_stub(bindir / "python3", "3.9.12")
            env = os.environ.copy()
            env.update(
                {
                    "PATH": f"{bindir}:/bin:/usr/bin",
                    "AXXON_TG_DRY_RUN": "1",
                    "TG_BOT_TOKEN": "token",
                    "AXXON_HOST": "example.local",
                    "AXXON_PASS": "secret",
                }
            )
            result = subprocess.run(
                [str(RUN_SCRIPT)],
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Python 3.11+", result.stderr)
        self.assertIn("AXXON_TG_PYTHON_BIN", result.stderr)


if __name__ == "__main__":
    unittest.main()

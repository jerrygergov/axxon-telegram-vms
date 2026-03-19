import json
import subprocess
import unittest
from unittest.mock import patch


class ProcessBridgeTests(unittest.TestCase):
    def _load_module(self):
        try:
            from scripts import process_bridge
        except ImportError as exc:  # pragma: no cover - exercised in red state
            self.fail(str(exc))
        return process_bridge

    def test_run_command_parses_json_stdout(self):
        process_bridge = self._load_module()

        with patch.object(process_bridge.subprocess, "run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=["tool"],
                returncode=0,
                stdout=json.dumps({"ok": True}),
                stderr="",
            )

            result = process_bridge.run_command(["tool"], timeout_sec=5)

        self.assertEqual(result.text, '{"ok": true}')
        self.assertEqual(result.parsed, {"ok": True})

    def test_run_command_falls_back_to_text(self):
        process_bridge = self._load_module()

        with patch.object(process_bridge.subprocess, "run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=["tool"],
                returncode=0,
                stdout="/tmp/file.jpg\n",
                stderr="",
            )

            result = process_bridge.run_command(["tool"], timeout_sec=5)

        self.assertEqual(result.text, "/tmp/file.jpg")
        self.assertEqual(result.parsed, "/tmp/file.jpg")

    def test_run_command_raises_timeout_error(self):
        process_bridge = self._load_module()

        with patch.object(process_bridge.subprocess, "run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired(cmd=["tool"], timeout=9)

            with self.assertRaises(process_bridge.CommandExecutionError) as ctx:
                process_bridge.run_command(["tool"], timeout_sec=9)

        self.assertIn("timed out", str(ctx.exception))

    def test_run_command_raises_non_zero_error_with_stderr(self):
        process_bridge = self._load_module()

        with patch.object(process_bridge.subprocess, "run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=["tool"],
                returncode=2,
                stdout="",
                stderr="broken",
            )

            with self.assertRaises(process_bridge.CommandExecutionError) as ctx:
                process_bridge.run_command(["tool"], timeout_sec=5)

        self.assertIn("broken", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass(frozen=True)
class CommandResult:
    text: str
    parsed: object


class CommandExecutionError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        command: Sequence[str],
        timeout_sec: int,
        returncode: int | None = None,
        stdout: str = "",
        stderr: str = "",
    ):
        super().__init__(message)
        self.command = tuple(command)
        self.timeout_sec = timeout_sec
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def run_command(cmd: Sequence[str], *, timeout_sec: int, cwd: str | Path | None = None) -> CommandResult:
    try:
        proc = subprocess.run(
            list(cmd),
            text=True,
            capture_output=True,
            timeout=timeout_sec,
            cwd=cwd,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise CommandExecutionError(
            f"Command timed out after {timeout_sec}s",
            command=cmd,
            timeout_sec=timeout_sec,
            stdout=str(getattr(exc, "stdout", "") or ""),
            stderr=str(getattr(exc, "stderr", "") or ""),
        ) from exc

    stdout = str(proc.stdout or "")
    stderr = str(proc.stderr or "")
    if proc.returncode != 0:
        detail = (stderr or stdout).strip() or f"exit {proc.returncode}"
        raise CommandExecutionError(
            detail,
            command=cmd,
            timeout_sec=timeout_sec,
            returncode=proc.returncode,
            stdout=stdout,
            stderr=stderr,
        )

    text = stdout.strip()
    try:
        parsed = json.loads(text)
    except Exception:
        parsed = text
    return CommandResult(text=text, parsed=parsed)

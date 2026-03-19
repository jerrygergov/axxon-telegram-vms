"""Pure live-session job primitives extracted from the script runtime."""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from typing import Awaitable, Callable


@dataclass
class LiveSessionRecord:
    user_id: int
    camera_idx: int
    chat_id: int
    message_id: int
    session_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    started_at_monotonic: float = field(default=0.0)


class LiveSessionRuntime:
    def __init__(
        self,
        runner: Callable[[LiveSessionRecord], Awaitable[None]],
        on_end: Callable[[LiveSessionRecord, str], Awaitable[None] | None] | None = None,
    ):
        self._runner = runner
        self._on_end = on_end
        self._sessions: dict[int, LiveSessionRecord] = {}
        self._tasks: dict[int, asyncio.Task] = {}
        self._stop_reasons: dict[int, str] = {}

    def get(self, user_id: int) -> LiveSessionRecord | None:
        return self._sessions.get(user_id)

    def active_count(self) -> int:
        return len(self._sessions)

    async def start(self, rec: LiveSessionRecord) -> bool:
        replaced = False
        if rec.user_id in self._sessions:
            replaced = await self.stop(rec.user_id, reason="replaced") is not None
        rec.started_at_monotonic = asyncio.get_running_loop().time()
        self._sessions[rec.user_id] = rec
        self._tasks[rec.user_id] = asyncio.create_task(self._run_session(rec))
        return replaced

    async def stop(self, user_id: int, reason: str = "manual") -> LiveSessionRecord | None:
        rec = self._sessions.get(user_id)
        task = self._tasks.get(user_id)
        if not rec:
            return None
        self._stop_reasons[user_id] = reason
        if task and not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            except Exception:
                pass
        self._tasks.pop(user_id, None)
        self._sessions.pop(user_id, None)
        self._stop_reasons.pop(user_id, None)
        return rec

    async def _run_session(self, rec: LiveSessionRecord) -> None:
        reason = "finished"
        try:
            await self._runner(rec)
        except asyncio.CancelledError:
            reason = self._stop_reasons.get(rec.user_id, "cancelled")
            raise
        except Exception:
            reason = "error"
            raise
        finally:
            current = self._sessions.get(rec.user_id)
            if current and current.session_id == rec.session_id:
                self._sessions.pop(rec.user_id, None)
                self._tasks.pop(rec.user_id, None)
                self._stop_reasons.pop(rec.user_id, None)
            if self._on_end:
                maybe_coro = self._on_end(rec, reason)
                if asyncio.iscoroutine(maybe_coro):
                    await maybe_coro


__all__ = ["LiveSessionRecord", "LiveSessionRuntime"]

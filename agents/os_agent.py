# ============================================================
#  agents/os_agent.py  — Agent 5: OS & System Controller 💻
#  Controls macOS apps, files, terminal via Python + PyAutoGUI
# ============================================================

import os
import subprocess
import asyncio
from pathlib import Path
from .base import BaseAgent
from rich.console import Console

console = Console()


class OSAgent(BaseAgent):
    agent_id = "os_ctrl"

    async def execute(self, intent: str, params: dict, raw: str) -> str:
        intent_lower = intent.lower()

        if "open" in intent_lower:
            return self._open_app(params.get("app", self._extract_app(raw)))

        if "close" in intent_lower or "quit" in intent_lower:
            return self._close_app(params.get("app", self._extract_app(raw)))

        if "screenshot" in intent_lower:
            return self._take_screenshot()

        if "volume" in intent_lower:
            level = params.get("level", 50)
            return self._set_volume(int(level))

        if any(k in intent_lower for k in ["terminal", "run command", "execute"]):
            cmd = params.get("command", "")
            if cmd:
                return self._run_terminal(cmd)

        if any(k in intent_lower for k in ["file", "folder", "directory"]):
            return self._file_op(intent, params)

        return f"OS Agent ready. Command not matched: '{intent}'"

    # ── App control ──────────────────────────────────────────
    def _open_app(self, app: str) -> str:
        if not app:
            return "Boss, which app should I open?"
        try:
            subprocess.Popen(["open", "-a", app])
            return f"Opening {app}, Boss."
        except Exception as e:
            return f"Could not open {app}: {e}"

    def _close_app(self, app: str) -> str:
        if not app:
            return "Boss, which app should I close?"
        try:
            subprocess.run(["osascript", "-e",
                            f'tell application "{app}" to quit'])
            return f"{app} closed."
        except Exception as e:
            return f"Could not close {app}: {e}"

    # ── Screenshot ───────────────────────────────────────────
    def _take_screenshot(self) -> str:
        path = os.path.expanduser("~/Desktop/jarvis_screenshot.png")
        subprocess.run(["screencapture", "-x", path])
        return f"Screenshot saved to Desktop as jarvis_screenshot.png"

    # ── Volume ───────────────────────────────────────────────
    def _set_volume(self, level: int) -> str:
        level = max(0, min(100, level))
        subprocess.run([
            "osascript", "-e",
            f"set volume output volume {level}"
        ])
        return f"Volume set to {level}%, Boss."

    # ── Terminal command ─────────────────────────────────────
    def _run_terminal(self, cmd: str) -> str:
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=30
            )
            out = result.stdout.strip() or result.stderr.strip()
            return out[:400] if out else "Command executed. No output."
        except subprocess.TimeoutExpired:
            return "Command timed out after 30 seconds."
        except Exception as e:
            return f"Terminal error: {e}"

    # ── File operations ──────────────────────────────────────
    def _file_op(self, intent: str, params: dict) -> str:
        path = params.get("path", "")
        if not path:
            return f"File task noted: '{intent}'. Please specify a path."
        p = Path(os.path.expanduser(path))
        if p.exists():
            return f"Found: {p}  |  Size: {p.stat().st_size} bytes"
        return f"Path not found: {path}"

    # ── Utility ──────────────────────────────────────────────
    def _extract_app(self, raw: str) -> str:
        """Best-effort: grab the word after 'open' or 'close'."""
        words = raw.lower().split()
        for trigger in ("open", "close", "quit", "launch"):
            if trigger in words:
                idx = words.index(trigger)
                if idx + 1 < len(words):
                    return words[idx + 1].capitalize()
        return ""

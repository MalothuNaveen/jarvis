# ============================================================
#  agents/devops_agent.py  — Agent 7: Self-Healing DevOps Agent 🛠️
#  Watches VS Code folders, reads errors, auto-fixes via Llama 3
# ============================================================

import os
import asyncio
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events    import FileSystemEventHandler
from .base import BaseAgent
from rich.console import Console
import ollama as _ollama
from config import OLLAMA_MODEL

console = Console()

# ── Filesystem watcher ────────────────────────────────────────
class _CodeWatcher(FileSystemEventHandler):
    def __init__(self, watch_path: str):
        self.watch_path = watch_path
        self.last_error: str = ""

    def on_modified(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith((".py", ".ts", ".js", ".go")):
            console.print(f"[dim]📁 File changed: {event.src_path}[/dim]")


_watchers: dict[str, Observer] = {}

def start_watching(path: str) -> None:
    if path in _watchers:
        return
    handler  = _CodeWatcher(path)
    observer = Observer()
    observer.schedule(handler, path, recursive=True)
    observer.daemon = True
    observer.start()
    _watchers[path] = observer
    console.print(f"[green]👁️  Watching: {path}[/green]")


# ── Agent ─────────────────────────────────────────────────────
class DevOpsAgent(BaseAgent):
    agent_id = "devops"

    async def execute(self, intent: str, params: dict, raw: str) -> str:
        intent_lower = intent.lower()

        if "watch" in intent_lower:
            path = params.get("path", os.path.expanduser("~/Developer"))
            start_watching(os.path.expanduser(path))
            return f"Now watching {path} for code changes, Boss."

        if any(k in intent_lower for k in ["fix", "error", "bug", "crash"]):
            error = params.get("error", raw)
            return await self._auto_fix(error, params)

        if "git" in intent_lower:
            return self._git_op(intent, params)

        if "run" in intent_lower or "test" in intent_lower:
            cmd = params.get("command", "")
            return self._run_cmd(cmd)

        return f"DevOps Agent ready. Say 'fix this error: <message>' or 'watch my project'."

    # ── Auto-fix via Llama 3 ─────────────────────────────────
    async def _auto_fix(self, error: str, params: dict) -> str:
        file_path = params.get("file", "")
        code_context = ""

        if file_path and os.path.exists(os.path.expanduser(file_path)):
            with open(os.path.expanduser(file_path)) as f:
                code_context = f.read()[:3000]  # Send max 3K chars

        code_section = ("Code context:\n" + code_context) if code_context else ""
        prompt = f"""
You are a senior developer. Fix the following error.
Return ONLY the corrected code (no prose, no markdown fences).

Error:
{error}

{code_section}
""".strip()

        try:
            response = _ollama.chat(
                model=OLLAMA_MODEL,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.1},
            )
            fix = response["message"]["content"].strip()

            # If file path given, apply the fix
            if file_path and code_context:
                out_path = os.path.expanduser(file_path)
                with open(out_path, "w") as f:
                    f.write(fix)
                return f"Boss, bug fixed and saved to {file_path}. Review and push when ready."

            console.print(f"[cyan]Suggested fix:\n{fix[:600]}[/cyan]")
            return "Boss, I've analyzed the error and printed the fix above. Apply it?"

        except Exception as e:
            return f"DevOps auto-fix error: {e}"

    # ── Git operations ────────────────────────────────────────
    def _git_op(self, intent: str, params: dict) -> str:
        repo  = params.get("repo", ".")
        op    = params.get("op", "status")
        cmds  = {
            "status": ["git", "status"],
            "pull"  : ["git", "pull"],
            "push"  : ["git", "push"],
            "log"   : ["git", "log", "--oneline", "-10"],
        }
        cmd = cmds.get(op, ["git", "status"])
        try:
            result = subprocess.run(
                cmd, cwd=os.path.expanduser(repo),
                capture_output=True, text=True, timeout=30
            )
            return (result.stdout or result.stderr).strip()[:400]
        except Exception as e:
            return f"Git error: {e}"

    # ── Run arbitrary command ─────────────────────────────────
    def _run_cmd(self, cmd: str) -> str:
        if not cmd:
            return "Please specify a command to run."
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True,
                text=True, timeout=60
            )
            out = result.stdout.strip() or result.stderr.strip()
            return out[:500] if out else f"Done: {cmd}"
        except Exception as e:
            return f"Command error: {e}"

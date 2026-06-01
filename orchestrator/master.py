# ============================================================
#  orchestrator/master.py
#  Master Orchestrator — The Brain 🧠
#  Parses intent via Llama 3 (Ollama) → routes to correct agent
# ============================================================

import json
import subprocess
import asyncio
from datetime import datetime
from rich.console import Console
from rich.panel  import Panel

import ollama as _ollama

from config import (
    OLLAMA_MODEL, OLLAMA_TIMEOUT, TTS_VOICE, TTS_RATE,
    AGENT_COMMS, AGENT_BROWSER, AGENT_MOBILE,
    AGENT_OS, AGENT_MULTIMEDIA, AGENT_DEVOPS, AGENT_INTELLIGENCE,
)

console = Console()

# ── System prompt that teaches Llama 3 how to route ──────────
ROUTER_SYSTEM_PROMPT = """
You are JARVIS, a personal AI assistant running 100% locally on a Mac M1 Pro.
You receive a voice command from the user and must decide which agent to route it to.

Available agents and their responsibilities:
- comms        : Gmail reading/sending, WhatsApp messaging, drafting replies
- browser      : Open URLs, fill forms, web login, download files from websites
- mobile       : OTP capture, phone call/SMS alerts, mobile sync
- os_ctrl      : Open/close apps, manage files, take screenshots, system volume, terminal commands
- multimedia   : Photo/video search, image editing, gallery management
- devops       : Fix code bugs, run git commands, watch VS Code errors, GitHub pipelines
- intelligence : News, trending topics, weather, GitHub trending, tech updates

Respond ONLY with a valid JSON object — no prose, no markdown fences:
{
  "agent": "<agent_id>",
  "intent": "<one sentence summary of what the user wants>",
  "params": { ... }
}

If the command needs multiple agents, pick the PRIMARY one only.
If unclear, route to "os_ctrl" as default.
"""


# ── Agent registry (populated by main.py) ───────────────────
_agent_registry: dict = {}

def register_agent(agent_id: str, agent_instance) -> None:
    _agent_registry[agent_id] = agent_instance


# ── LLM routing ─────────────────────────────────────────────
def route_command(command: str) -> dict:
    """
    Send command to Llama 3 via Ollama.
    Returns parsed routing dict: {agent, intent, params}
    """
    try:
        response = _ollama.chat(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": ROUTER_SYSTEM_PROMPT},
                {"role": "user",   "content": command},
            ],
            options={"temperature": 0.1},
        )
        raw = response["message"]["content"].strip()

        # Strip accidental markdown fences
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        routing = json.loads(raw)
        return routing

    except json.JSONDecodeError as e:
        console.print(f"[red]Router JSON parse error: {e}[/red]")
        return {"agent": "os_ctrl", "intent": command, "params": {}}
    except Exception as e:
        console.print(f"[red]Ollama error: {e}[/red]")
        return {"agent": "os_ctrl", "intent": command, "params": {}}


# ── TTS (macOS built-in, zero cost) ─────────────────────────
def speak(text: str) -> None:
    """Use macOS 'say' command — no API, no latency, fully offline."""
    clean = text.replace('"', "'")
    subprocess.Popen(
        ["say", "-v", TTS_VOICE, "-r", str(TTS_RATE), clean],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


# ── Dispatch ─────────────────────────────────────────────────
async def dispatch(command: str) -> str:
    """
    Full pipeline:
      command → Llama 3 routing → agent.execute() → TTS response
    Returns agent's text response.
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    console.print(Panel(
        f"[bold cyan]{command}[/bold cyan]",
        title=f"[white]🎤 Command [{timestamp}][/white]",
        border_style="cyan"
    ))

    # 1. Route via LLM
    routing = route_command(command)
    agent_id = routing.get("agent", "os_ctrl")
    intent   = routing.get("intent", command)
    params   = routing.get("params", {})

    console.print(
        f"[yellow]→ Routing to[/yellow] [bold]{agent_id}[/bold]  "
        f"[dim]| intent: {intent}[/dim]"
    )

    # 2. Execute on registered agent
    agent = _agent_registry.get(agent_id)
    if agent is None:
        response = f"Agent '{agent_id}' is not yet initialized, Boss."
        console.print(f"[red]{response}[/red]")
    else:
        try:
            response = await agent.execute(intent=intent, params=params, raw=command)
        except Exception as e:
            response = f"Error in {agent_id}: {e}"
            console.print(f"[red]{response}[/red]")

    # 3. Speak + print response
    console.print(Panel(
        f"[green]{response}[/green]",
        title="[white]🤖 JARVIS[/white]",
        border_style="green"
    ))
    speak(response)

    return response


# ── Sync wrapper (for non-async callers) ────────────────────
def handle_command(command: str) -> str:
    return asyncio.run(dispatch(command))

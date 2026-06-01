#!/usr/bin/env python3
# ============================================================
#  JARVIS — Local 8-Agent AI System
#  Mac M1 Pro | 100% Local | Zero Cost | Full Privacy
#
#  Run:  python main.py
#  Modes:
#    --voice   : Continuous wake-word listening  (default)
#    --text    : Type commands in terminal
#    --once    : Listen for one command then exit
# ============================================================

import sys
import asyncio
import argparse
from rich.console import Console
from rich.panel   import Panel
from rich.text    import Text

# ── Internal imports ─────────────────────────────────────────
from config import WAKE_WORD
from orchestrator.master import dispatch, register_agent, speak
from orchestrator.voice  import listen_for_wake_word, listen_once
from agents import (
    CommsAgent, BrowserAgent, MobileAgent, start_webhook_server,
    OSAgent, MultimediaAgent, DevOpsAgent, IntelligenceAgent,
)

console = Console()


# ── Banner ────────────────────────────────────────────────────
def print_banner():
    banner = Text()
    banner.append("  ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗\n", style="bold cyan")
    banner.append("  ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝\n", style="bold cyan")
    banner.append("  ██║███████║██████╔╝██║   ██║██║███████╗\n", style="bold blue")
    banner.append("  ██ ╝██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║\n", style="bold blue")
    banner.append("  ╚██████╔╝██║  ██║ ╚████╔╝ ██║███████║\n", style="bold magenta")
    banner.append("   ╚═════╝ ╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝\n", style="bold magenta")
    banner.append("\n  Local 8-Agent AI System  |  Mac M1 Pro  |  Zero Cost\n",
                  style="dim white")

    console.print(Panel(banner, border_style="cyan", padding=(0, 2)))


# ── Initialise all agents ─────────────────────────────────────
def init_agents():
    console.print("[bold yellow]Initialising agents...[/bold yellow]")

    agents = [
        CommsAgent(),
        BrowserAgent(),
        MobileAgent(),
        OSAgent(),
        MultimediaAgent(),
        DevOpsAgent(),
        IntelligenceAgent(),
    ]

    for agent in agents:
        register_agent(agent.agent_id, agent)
        console.print(f"  [green]✓[/green] {agent.agent_id}")

    # Start mobile OTP webhook on background thread
    start_webhook_server(port=8765)

    console.print(f"[bold green]All 8 agents ready.[/bold green]\n")


# ── Modes ─────────────────────────────────────────────────────
def run_voice_mode():
    """Continuous wake-word loop — 'Jarvis <command>'"""
    console.print(
        f"[bold cyan]🎤 Voice mode active.[/bold cyan]  "
        f"Say [bold yellow]'{WAKE_WORD}'[/bold yellow] to activate.\n"
    )
    speak(f"JARVIS online. Say {WAKE_WORD} followed by your command.")

    def on_command(cmd: str):
        asyncio.get_event_loop().run_until_complete(dispatch(cmd))

    listen_for_wake_word(on_command)


def run_text_mode():
    """Interactive text loop — type commands in terminal."""
    console.print(
        "[bold cyan]💬 Text mode active.[/bold cyan]  "
        "Type a command and press Enter.  Type [bold red]exit[/bold red] to quit.\n"
    )
    speak("JARVIS text mode activated.")

    while True:
        try:
            cmd = input("You: ").strip()
            if not cmd:
                continue
            if cmd.lower() in ("exit", "quit", "bye"):
                speak("Goodbye Boss.")
                break
            asyncio.get_event_loop().run_until_complete(dispatch(cmd))
        except (KeyboardInterrupt, EOFError):
            speak("Goodbye Boss.")
            break


def run_once_mode():
    """Listen for exactly one voice command, execute, then exit."""
    console.print("[bold cyan]🎤 Listening for one command...[/bold cyan]")
    speak("Ready. Speak your command.")
    cmd = listen_once()
    if cmd:
        asyncio.get_event_loop().run_until_complete(dispatch(cmd))


# ── Entry point ───────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="JARVIS Local AI System")
    parser.add_argument("--voice", action="store_true", help="Wake-word voice mode (default)")
    parser.add_argument("--text",  action="store_true", help="Interactive text mode")
    parser.add_argument("--once",  action="store_true", help="Listen for one command then exit")
    args = parser.parse_args()

    print_banner()
    init_agents()

    if args.text:
        run_text_mode()
    elif args.once:
        run_once_mode()
    else:
        # Default: voice mode
        run_voice_mode()


if __name__ == "__main__":
    main()

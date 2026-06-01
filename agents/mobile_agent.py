# ============================================================
#  agents/mobile_agent.py  — Agent 4: Mobile Sync & Notification Agent 📱🔐
#  Receives OTP, call & SMS alerts from Android via local Wi-Fi webhook
# ============================================================

import asyncio
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from .base import BaseAgent
from rich.console import Console

console = Console()

# ── Shared state (populated by webhook listener) ─────────────
_latest_otp:  str = ""
_latest_sms:  str = ""
_latest_call: str = ""


# ── Lightweight webhook server (runs in background thread) ───
class _WebhookHandler(BaseHTTPRequestHandler):
    """
    Android Tasker sends HTTP POST to http://<mac-ip>:8765/event
    Body format (JSON):
      {"type": "otp",  "value": "123456"}
      {"type": "sms",  "value": "Your package is out for delivery"}
      {"type": "call", "value": "Missed call from +91-9876543210"}
    """

    def do_POST(self):
        import json
        global _latest_otp, _latest_sms, _latest_call
        try:
            length = int(self.headers.get("Content-Length", 0))
            data   = json.loads(self.rfile.read(length))
            etype  = data.get("type", "")
            value  = data.get("value", "")

            if etype == "otp":
                _latest_otp = value
                console.print(f"[bold green]📱 OTP received: {value}[/bold green]")
            elif etype == "sms":
                _latest_sms = value
                console.print(f"[cyan]📩 SMS: {value}[/cyan]")
            elif etype == "call":
                _latest_call = value
                console.print(f"[magenta]📞 Call alert: {value}[/magenta]")

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        except Exception as e:
            console.print(f"[red]Webhook error: {e}[/red]")
            self.send_response(500)
            self.end_headers()

    def log_message(self, *args):
        pass  # silence default HTTP logs


def start_webhook_server(port: int = 8765) -> None:
    """Start the webhook listener in a daemon thread."""
    server = HTTPServer(("0.0.0.0", port), _WebhookHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    console.print(
        f"[green]📱 Mobile webhook listening on port {port}[/green]  "
        f"[dim](Configure Tasker on Android to POST here)[/dim]"
    )


# ── Agent ────────────────────────────────────────────────────
class MobileAgent(BaseAgent):
    agent_id = "mobile"

    async def execute(self, intent: str, params: dict, raw: str) -> str:
        intent_lower = intent.lower()

        if "otp" in intent_lower:
            return self._get_otp()
        if "sms" in intent_lower or "message" in intent_lower:
            return self._get_sms()
        if "call" in intent_lower:
            return self._get_call()

        return (
            f"Mobile Agent ready. Latest OTP: {_latest_otp or 'none'} | "
            f"SMS: {_latest_sms[:40] + '...' if len(_latest_sms) > 40 else _latest_sms or 'none'}"
        )

    def _get_otp(self) -> str:
        if _latest_otp:
            return f"Boss, latest OTP is {_latest_otp}"
        return "No OTP received yet, Boss. Waiting on phone..."

    def _get_sms(self) -> str:
        if _latest_sms:
            return f"Latest SMS: {_latest_sms}"
        return "No SMS received yet."

    def _get_call(self) -> str:
        if _latest_call:
            return f"Call alert: {_latest_call}"
        return "No call alerts yet."

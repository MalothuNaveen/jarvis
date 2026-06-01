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
_command_count: int = 0
_last_latency: int = 0

def record_command_execution(latency_ms: int):
    global _command_count, _last_latency
    _command_count += 1
    _last_latency = latency_ms

# ── Lightweight webhook server (runs in background thread) ───
class _WebhookHandler(BaseHTTPRequestHandler):
    """
    Handles Android Tasker webhooks and Jarvis HUD UI control commands & status checking.
    """

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        import json
        global _latest_otp, _latest_sms, _latest_call
        try:
            length = int(self.headers.get("Content-Length", 0))
            if length == 0:
                self.send_response(400)
                self.end_headers()
                return

            data   = json.loads(self.rfile.read(length))
            etype  = data.get("type", "")
            value  = data.get("value", "")

            # CORS headers helper
            def send_json_response(status_code, response_dict):
                self.send_response(status_code)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(response_dict).encode())

            if etype == "command":
                from orchestrator.master import handle_command
                import time
                t0 = time.time()
                response_text = handle_command(value)
                latency = int((time.time() - t0) * 1000)
                record_command_execution(latency)
                send_json_response(200, {"status": "success", "response": response_text})
                return

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
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(b"OK")
        except Exception as e:
            console.print(f"[red]Webhook error: {e}[/red]")
            self.send_response(500)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

    def do_GET(self):
        import json
        import psutil
        if self.path == "/status":
            try:
                cpu_pct = psutil.cpu_percent()
                mem_pct = psutil.virtual_memory().percent
                
                self.send_response(200)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                
                status_data = {
                    "status": "success",
                    "cpu": cpu_pct,
                    "memory": mem_pct,
                    "command_count": _command_count,
                    "llm_latency": _last_latency
                }
                self.wfile.write(json.dumps(status_data).encode())
            except Exception as e:
                console.print(f"[red]Status get error: {e}[/red]")
                self.send_response(500)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
        else:
            self.send_response(404)
            self.send_header("Access-Control-Allow-Origin", "*")
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

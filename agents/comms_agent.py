# ============================================================
#  agents/comms_agent.py  — Agent 2: Comms Agent 📧💬
#  Gmail (Google API) + WhatsApp (Playwright browser automation)
# ============================================================

from .base import BaseAgent
from rich.console import Console

console = Console()


class CommsAgent(BaseAgent):
    """
    Handles Gmail & WhatsApp read / draft / send operations.

    Capabilities (extend each method below):
    - Read latest emails / WhatsApp messages
    - Draft smart replies using Llama 3
    - Send Gmail via Google API (free OAuth token)
    - Send WhatsApp via Playwright browser automation
    """

    agent_id = "comms"

    async def execute(self, intent: str, params: dict, raw: str) -> str:
        intent_lower = intent.lower()

        if any(k in intent_lower for k in ["email", "gmail", "mail", "inbox"]):
            return await self._handle_gmail(intent, params)

        if any(k in intent_lower for k in ["whatsapp", "message", "chat", "wa"]):
            return await self._handle_whatsapp(intent, params)

        return f"Comms Agent received: '{intent}'. Please specify gmail or whatsapp."

    # ── Gmail ────────────────────────────────────────────────
    async def _handle_gmail(self, intent: str, params: dict) -> str:
        """
        TODO: Implement Gmail OAuth flow.

        Quickstart:
          pip install google-auth-oauthlib google-api-python-client
          Follow: https://developers.google.com/gmail/api/quickstart/python
          Save credentials.json to jarvis/secrets/gmail_credentials.json
        """
        # Stub — replace with real Gmail API calls
        console.print("[yellow][CommsAgent] Gmail handler — stub active[/yellow]")
        to      = params.get("to", "your recipient")
        subject = params.get("subject", "No Subject")
        body    = params.get("body", intent)
        return (
            f"Boss, Gmail draft ready. To: {to} | Subject: {subject}. "
            f"Shall I send it? (Say 'yes send' to confirm)"
        )

    # ── WhatsApp ─────────────────────────────────────────────
    async def _handle_whatsapp(self, intent: str, params: dict) -> str:
        """
        TODO: Implement WhatsApp Web via Playwright.

        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            await page.goto("https://web.whatsapp.com")
            # Scan QR once; session persists in user_data_dir
        """
        console.print("[yellow][CommsAgent] WhatsApp handler — stub active[/yellow]")
        contact = params.get("contact", "the contact")
        message = params.get("message", intent)
        return (
            f"Boss, WhatsApp message drafted for {contact}: '{message}'. "
            f"Say 'send it' to confirm."
        )

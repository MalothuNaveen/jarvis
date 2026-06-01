# ============================================================
#  agents/comms_agent.py  — Agent 2: Comms Agent 📧💬
#  Gmail, Outlook, WhatsApp (Playwright) & Microsoft Teams
# ============================================================

import os
import urllib.parse
import subprocess
from .base import BaseAgent
from rich.console import Console
from playwright.async_api import async_playwright
from config import BASE_DIR

console = Console()


class CommsAgent(BaseAgent):
    """
    Handles Gmail, Outlook, WhatsApp & Microsoft Teams operations.
    """

    agent_id = "comms"

    async def execute(self, intent: str, params: dict, raw: str) -> str:
        intent_lower = intent.lower()

        if "outlook" in intent_lower:
            return await self._handle_outlook(intent, params)

        if any(k in intent_lower for k in ["email", "gmail", "mail", "inbox"]):
            return await self._handle_gmail(intent, params)

        if "teams" in intent_lower:
            return await self._handle_teams(intent, params)

        if any(k in intent_lower for k in ["whatsapp", "message", "chat", "wa"]):
            return await self._handle_whatsapp(intent, params)

        return f"Comms Agent received: '{intent}'."

    # ── Gmail ────────────────────────────────────────────────
    async def _handle_gmail(self, intent: str, params: dict) -> str:
        """
        Gmail handler (uses web compose fallback for now).
        """
        console.print("[yellow][CommsAgent] Gmail handler active[/yellow]")
        to      = params.get("to", "")
        subject = params.get("subject", "No Subject")
        body    = params.get("body", intent)
        
        web_url = f"https://mail.google.com/mail/?view=cm&fs=1&to={urllib.parse.quote(to)}&su={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
        subprocess.run(["open", web_url])
        return f"Gmail compose window opened in browser to send mail to {to}."

    # ── Outlook ──────────────────────────────────────────────
    async def _handle_outlook(self, intent: str, params: dict) -> str:
        """
        Outlook handler (uses native macOS Outlook App via AppleScript if available).
        """
        console.print("[yellow][CommsAgent] Outlook handler active[/yellow]")
        to      = params.get("to", "")
        subject = params.get("subject", "No Subject")
        body    = params.get("body", intent)

        # Check if Microsoft Outlook app is installed
        outlook_check = subprocess.run(
            ["osascript", "-e", 'id of application "Microsoft Outlook"'],
            capture_output=True, text=True
        )

        if outlook_check.returncode == 0:
            # AppleScript to create Outlook mail draft
            applescript = f'''
            tell application "Microsoft Outlook"
                set newMessage to make new outgoing message with properties {{subject:"{subject}", content:"{body}"}}
                make new recipient at newMessage with properties {{email address:{{address:"{to}"}}}}
                open newMessage
                activate
            end tell
            '''
            subprocess.run(["osascript", "-e", applescript])
            return f"Drafted email in Microsoft Outlook desktop app to: '{to}'."
        else:
            # Fallback: Open Outlook Web
            web_url = f"https://outlook.office.com/mail/deeplink/compose?to={urllib.parse.quote(to)}&subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
            subprocess.run(["open", web_url])
            return f"Outlook desktop app not found. Opened Outlook Web compose page."

    # ── Microsoft Teams ──────────────────────────────────────
    async def _handle_teams(self, intent: str, params: dict) -> str:
        """
        Microsoft Teams handler.
        """
        console.print("[yellow][CommsAgent] Teams handler active[/yellow]")
        contact = params.get("contact", "")
        message = params.get("message", "")

        teams_check = subprocess.run(
            ["osascript", "-e", 'id of application "Microsoft Teams"'],
            capture_output=True, text=True
        )

        if teams_check.returncode == 0:
            # Native Teams app launch & focus
            subprocess.run(["osascript", "-e", 'tell application "Microsoft Teams" to activate'])
            return f"Launched Microsoft Teams desktop app. Please message {contact}."
        else:
            # Fallback: Open Teams Web
            subprocess.run(["open", "https://teams.microsoft.com"])
            return f"Microsoft Teams desktop app not found. Opened Teams Web portal."

    # ── WhatsApp ─────────────────────────────────────────────
    async def _handle_whatsapp(self, intent: str, params: dict) -> str:
        """
        WhatsApp Web automation using Playwright.
        """
        contact = params.get("contact", "")
        message = params.get("message", "")

        # Fallback to parse contact/message from intent if Llama returned it empty
        if not contact:
            # Split and find words after 'to' or 'message'
            words = intent.split()
            if "to" in words:
                idx = words.index("to")
                if idx + 1 < len(words):
                    contact = words[idx + 1].capitalize()
            if not contact:
                return "Please specify the contact name for the WhatsApp message."

        if not message:
            message = intent

        session_dir = os.path.join(BASE_DIR, "secrets", "whatsapp_session")
        os.makedirs(session_dir, exist_ok=True)

        console.print(f"[bold green]Opening WhatsApp Web to message '{contact}'...[/bold green]")

        async with async_playwright() as p:
            # We run with headless=False so the user can scan QR code on first launch
            browser = await p.chromium.launch_persistent_context(
                user_data_dir=session_dir,
                headless=False,
                args=["--no-sandbox"]
            )
            page = await browser.new_page()
            await page.goto("https://web.whatsapp.com")

            # Wait for search box to load (indicates login is successful)
            search_box_selector = 'div[contenteditable="true"][data-tab="3"]'
            console.print("[yellow]Waiting for WhatsApp Web login... If you see the QR code, please scan it with your phone.[/yellow]")

            try:
                # Wait up to 60s for QR scan / page load
                await page.wait_for_selector(search_box_selector, timeout=60000)
            except Exception:
                await browser.close()
                return "WhatsApp Web login timed out. Please run the command again and scan the QR code."

            console.print("[green]Logged into WhatsApp Web successfully.[/green]")

            # 1. Search for contact name
            await page.click(search_box_selector)
            await page.fill(search_box_selector, contact)
            await page.keyboard.press("Enter")

            # 2. Wait for chat window to load
            await page.wait_for_timeout(2000)

            # 3. Locate message text box
            message_box_selector = 'div[contenteditable="true"][data-tab="10"]'

            try:
                await page.wait_for_selector(message_box_selector, timeout=5000)
                await page.click(message_box_selector)
                await page.fill(message_box_selector, message)
                await page.keyboard.press("Enter")
                await page.wait_for_timeout(2500) # wait briefly to ensure message sends
                await browser.close()
                return f"WhatsApp message sent to {contact} successfully: '{message}'"
            except Exception as e:
                await browser.close()
                return f"Failed to locate message box for {contact}. Make sure the contact exists in your chat list."

#!/bin/bash
# ============================================================
#  JARVIS — One-time setup script for Mac M1 Pro
#  Run:  chmod +x setup.sh && ./setup.sh
# ============================================================

set -e
echo ""
echo "========================================"
echo "  JARVIS Setup  |  Mac M1 Pro"
echo "========================================"
echo ""

# 1. Ollama (local LLM server)
if ! command -v ollama &> /dev/null; then
  echo "→ Installing Ollama..."
  curl -fsSL https://ollama.ai/install.sh | sh
else
  echo "✓ Ollama already installed"
fi

echo "→ Pulling Llama 3 model (once, ~4.7 GB)..."
ollama pull llama3

# 2. Python dependencies
echo "→ Installing Python packages..."
pip install -r requirements.txt --break-system-packages

# 3. Playwright browsers
echo "→ Installing Playwright Chromium..."
playwright install chromium

# 4. Create secrets folder
mkdir -p secrets
echo "✓ secrets/ folder created (put gmail_credentials.json here)"

echo ""
echo "========================================"
echo "  Setup complete! Run JARVIS with:"
echo "  python main.py          # voice mode"
echo "  python main.py --text   # text mode"
echo "========================================"

# ============================================================
#  JARVIS — Local 8-Agent AI System
#  Dockerfile  |  Mac M1 Pro (ARM64) + x86_64 compatible
# ============================================================

FROM python:3.11-slim

# ── System dependencies ──────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    wget \
    ffmpeg \
    libsndfile1 \
    libasound2-dev \
    portaudio19-dev \
    build-essential \
    libssl-dev \
    libffi-dev \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# ── Working directory ────────────────────────────────────────
WORKDIR /app

# ── Copy project files ───────────────────────────────────────
COPY requirements.txt .
COPY config.py .
COPY main.py .
COPY setup.sh .
COPY orchestrator/ ./orchestrator/
COPY agents/ ./agents/
COPY README.md .
COPY jarvis_hud_ultra.html .

# ── Create runtime directories ───────────────────────────────
RUN mkdir -p logs memory secrets

# ── Install Python packages ──────────────────────────────────
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
        ollama \
        openai-whisper \
        numpy \
        scipy \
        sounddevice \
        browser-use \
        playwright \
        httpx \
        beautifulsoup4 \
        feedparser \
        watchdog \
        gitpython \
        Pillow \
        moviepy \
        python-dotenv \
        rich

# ── Install Playwright Chromium ──────────────────────────────
RUN playwright install chromium && \
    playwright install-deps chromium

# ── Expose ports ─────────────────────────────────────────────
# 8765 → Mobile OTP webhook (Android Tasker)
# 8080 → HUD Dashboard web server (optional)
EXPOSE 8765 8080

# ── Health check ─────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8765/ || exit 1

# ── Entrypoint ───────────────────────────────────────────────
# Default: text mode (safe inside container — no mic access)
# Override with: docker run jarvis python main.py --voice
CMD ["python", "main.py", "--text"]

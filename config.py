# ============================================================
#  JARVIS - Local 8-Agent System | config.py
#  Mac M1 Pro · 100% Local · Zero Cost · Full Privacy
# ============================================================

# ── Ollama / LLM ────────────────────────────────────────────
OLLAMA_BASE_URL   = "http://localhost:11434"
OLLAMA_MODEL      = "llama3"          # or llama3.1, mistral, etc.
OLLAMA_TIMEOUT    = 60                # seconds

# ── Whisper STT ─────────────────────────────────────────────
WHISPER_MODEL     = "base"            # tiny | base | small | medium
WHISPER_LANGUAGE  = "en"             # or "te" for Telugu, "hi" for Hindi
WAKE_WORD         = "jarvis"         # Say "Jarvis ..." to trigger

# ── Audio recording ─────────────────────────────────────────
SAMPLE_RATE       = 16000
RECORD_SECONDS    = 5                 # Max listen window per utterance
SILENCE_THRESHOLD = 500              # RMS below this = silence

# ── TTS (macOS built-in, zero cost) ─────────────────────────
TTS_VOICE         = "Samantha"       # macOS voice name
TTS_RATE          = 180              # words per minute

# ── Agent IDs  ──────────────────────────────────────────────
AGENT_COMMS         = "comms"
AGENT_BROWSER       = "browser"
AGENT_MOBILE        = "mobile"
AGENT_OS            = "os_ctrl"
AGENT_MULTIMEDIA    = "multimedia"
AGENT_DEVOPS        = "devops"
AGENT_INTELLIGENCE  = "intelligence"

ALL_AGENTS = [
    AGENT_COMMS,
    AGENT_BROWSER,
    AGENT_MOBILE,
    AGENT_OS,
    AGENT_MULTIMEDIA,
    AGENT_DEVOPS,
    AGENT_INTELLIGENCE,
]

# ── Paths ────────────────────────────────────────────────────
import os
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR   = os.path.join(BASE_DIR, "logs")
MEMORY_DIR = os.path.join(BASE_DIR, "memory")

os.makedirs(LOGS_DIR,   exist_ok=True)
os.makedirs(MEMORY_DIR, exist_ok=True)

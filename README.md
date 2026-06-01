# 🤖 JARVIS — Local 8-Agent AI System

> **Mac M1 Pro | 100% Local | Zero Cost | Full Privacy**  
> No OpenAI API. No subscriptions. Everything runs on your machine.

---

## 📁 Project Structure

```
jarvis/
├── main.py                    ← Start చేయడానికి ఇక్కడ నుండి run చెయ్యి
├── config.py                  ← అన్ని settings ఇక్కడ మార్చు
├── setup.sh                   ← First time install script
├── requirements.txt           ← Python packages list
├── orchestrator/
│   ├── master.py              ← 🧠 Brain: Llama 3 router + TTS
│   └── voice.py               ← 🎤 Whisper STT + wake-word listener
└── agents/
    ├── base.py                ← Base class (don't edit)
    ├── comms_agent.py         ← 📧 Gmail + WhatsApp
    ├── browser_agent.py       ← 🌐 Browser automation
    ├── mobile_agent.py        ← 📱 OTP + SMS + Call alerts
    ├── os_agent.py            ← 💻 Mac apps + files + terminal
    ├── multimedia_agent.py    ← 🎨 Photos + Videos
    ├── devops_agent.py        ← 🛠️ Code fix + Git + Watcher
    └── intelligence_agent.py ← 🌍 News + Weather + GitHub
```

---

## ⚡ Quick Start (First Time Setup)

### Step 1 — Install Ollama (Local LLM Server)
```bash
# Terminal లో run చెయ్యి:
curl -fsSL https://ollama.ai/install.sh | sh

# Llama 3 model download చెయ్యి (~4.7 GB, once only):
ollama pull llama3

# Ollama server start చెయ్యి:
ollama serve
```

### Step 2 — Python Dependencies
```bash
cd jarvis
pip install -r requirements.txt --break-system-packages
playwright install chromium
```

### Step 3 — Run JARVIS
```bash
# Text mode (testing కి best — voice setup అక్కర్లేదు):
python main.py --text

# Voice mode (wake word "Jarvis" చెప్పి command ఇవ్వు):
python main.py

# Single command mode:
python main.py --once
```

---

## 🤖 All 8 Agents — How They Work

---

### 1. 🧠 Master Orchestrator (`orchestrator/master.py`)

**పని:** నువ్వు చెప్పిన command ని Llama 3 కి పంపి, ఏ agent కి route చేయాలో decide చేస్తుంది.

**How it works:**
```
Your Voice → Whisper STT → Text → Llama 3 (Ollama) → JSON routing → Correct Agent
```

**Example routing JSON Llama 3 returns:**
```json
{
  "agent": "comms",
  "intent": "Send email to manager about meeting",
  "params": {"to": "manager@company.com", "subject": "Meeting Update"}
}
```

**TTS:** macOS built-in `say` command వాడుతుంది — zero latency, zero cost.

**Config లో మార్చగలవు (`config.py`):**
```python
OLLAMA_MODEL = "llama3"     # llama3.1, mistral, phi3 కూడా వాడవచ్చు
WAKE_WORD    = "jarvis"     # మార్చాలంటే: "hey computer", "boss" etc.
TTS_VOICE    = "Samantha"   # macOS voices: Alex, Karen, Daniel etc.
```

---

### 2. 📧 Comms Agent (`agents/comms_agent.py`)

**పని:** Gmail చదవడం/పంపడం, WhatsApp messages draft చేయడం.

**How it works:**
- Gmail → Google Free OAuth token (credentials.json)
- WhatsApp → Playwright browser automation (WhatsApp Web)

**Setup — Gmail:**
```bash
# 1. Google Cloud Console → https://console.cloud.google.com
# 2. New Project create చెయ్యి
# 3. Gmail API enable చెయ్యి
# 4. OAuth 2.0 credentials download చెయ్యి
# 5. credentials.json ని jarvis/secrets/ లో save చెయ్యి
pip install google-auth-oauthlib google-api-python-client
```

**Setup — WhatsApp:**
```bash
# Playwright browser open అవుతుంది, QR code scan చెయ్యి (once only)
# Session automatically save అవుతుంది
```

**Example commands:**
```
"Jarvis, my manager ki meeting cancel email pampinchu"
"Jarvis, WhatsApp lo Ravi ki 'on my way' message pampinchu"
"Jarvis, inbox lo unna latest emails chupu"
```

---

### 3. 🌐 Browser Automation Agent (`agents/browser_agent.py`)

**పని:** మనిషి లాగే browser open చేసి websites navigate చేయడం, forms fill చేయడం.

**How it works:**
```
BrowserUse (AI library) → Playwright → Headless Chromium → Website
```

**Full implementation:**
```python
# agents/browser_agent.py లో _open_and_act() replace చెయ్యి:
from browser_use import Agent as BUAgent
from langchain_ollama import OllamaLLM

llm    = OllamaLLM(model="llama3")
agent  = BUAgent(task=intent, llm=llm)
result = await agent.run()
return result.final_result()
```

**Example commands:**
```
"Jarvis, LinkedIn lo my profile open chesi latest job apply cheyyi"
"Jarvis, Amazon lo iPhone 15 price check cheyyi"
"Jarvis, Google Forms lo my details fill cheyyi — link: <url>"
```

---

### 4. 📱 Mobile Sync Agent (`agents/mobile_agent.py`)

**పని:** Android phone నుండి OTP, SMS, Call alerts ని laptop కి real-time లో పంపడం.

**How it works:**
```
Android Tasker → HTTP POST → Mac (port 8765 webhook) → JARVIS
```

**Android Setup (Tasker app — free/paid):**
1. Tasker install చెయ్యి
2. New Profile → Event → Phone → SMS Received
3. Task → Net → HTTP Request
   - Method: POST
   - URL: `http://<your-mac-ip>:8765/event`
   - Body: `{"type":"otp","value":"%SMSRB"}`
4. OTP filter కి: Profile → Condition → `%SMSRB ~ *OTP*`

**Mac IP తెలుసుకోవడానికి:**
```bash
ipconfig getifaddr en0
```

**Example commands:**
```
"Jarvis, latest OTP cheppu"
"Jarvis, phone lo SMS unnaaya"
"Jarvis, missed calls unnaaya"
```

---

### 5. 💻 OS & System Controller (`agents/os_agent.py`)

**పని:** Mac apps, files, terminal, volume — అన్నీ control చేయడం.

**How it works:**
- `subprocess` + `osascript` (AppleScript) → macOS native control
- `PyAutoGUI` → mouse/keyboard automation

**Example commands:**
```
"Jarvis, VS Code open cheyyi"
"Jarvis, Spotify close cheyyi"
"Jarvis, screenshot teeyyi"
"Jarvis, volume 50 ki set cheyyi"
"Jarvis, terminal lo git status run cheyyi"
```

**Custom terminal commands:**
```python
# params లో "command" key pass cheyyi
# Example: {"command": "cd ~/project && npm run build"}
```

---

### 6. 🎨 Multimedia Agent (`agents/multimedia_agent.py`)

**పని:** Photos/videos search చేయడం, Quick Look లో చూపించడం, resize చేయడం.

**How it works:**
- File system scan → date/time based filtering
- macOS `qlmanage` → Quick Look preview
- Pillow → image resize/edit

**Semantic search (AI-based) add చేయడానికి:**
```bash
pip install transformers torch
# CLIP model వాడి "bike photos" లాంటి text query తో images match చేయవచ్చు
```

**Example commands:**
```
"Jarvis, last week photos chupu"
"Jarvis, Desktop lo screenshots list cheyyi"
"Jarvis, this image ni 800x600 ki resize cheyyi — path: ~/Desktop/photo.jpg"
```

---

### 7. 🛠️ DevOps Agent (`agents/devops_agent.py`)

**పని:** Code errors detect చేసి Llama 3 తో auto-fix చేయడం, Git operations, file watcher.

**How it works:**
```
Watchdog (file watcher) → Error detected → Llama 3 prompt → Fixed code → Save
```

**VS Code integration:**
```bash
# Terminal task గా run చెయ్యి:
python main.py --text
# Then type: "watch my project at ~/Developer/myapp"
```

**GitHub webhook setup:**
```bash
# GitHub Settings → Webhooks → Add webhook
# Payload URL: http://<your-ngrok-url>/github-webhook
# ngrok: ngrok http 8766
```

**Example commands:**
```
"Jarvis, ~/Developer/app/main.py lo error fix cheyyi — error: NameError line 42"
"Jarvis, git status chupu"
"Jarvis, my project watch cheyyi at ~/Developer/jarvis"
"Jarvis, pytest run cheyyi"
```

---

### 8. 🌍 Intelligence Agent (`agents/intelligence_agent.py`)

**పని:** News, weather, GitHub trending — free APIs, no keys needed.

**How it works:**
- Weather → `wttr.in` (free, no API key)
- News → RSS feeds (TechCrunch, HackerNews, AI News)
- GitHub Trending → HTML scraping (BeautifulSoup)

**Example commands:**
```
"Jarvis, today weather cheppu — Hyderabad"
"Jarvis, latest tech news cheppu"
"Jarvis, GitHub lo today trending projects enti"
"Jarvis, AI news update ivvu"
```

---

## 🔗 How Agents Talk to Each Other (Chain Reaction)

```
Example: "GitHub build fail — auto fix and notify team"

1. DevOps Agent   → Error detect + Llama 3 fix
2. OS Agent       → Terminal lo git push run cheyyi
3. Comms Agent    → WhatsApp lo team ki "Fixed ✅" message
4. Master Orch.   → "Boss, bug fixed and team notified"
```

Master Orchestrator ప్రతి step కి voice update ఇస్తుంది.

---

## ⚙️ Configuration Reference (`config.py`)

| Setting | Default | Description |
|---------|---------|-------------|
| `OLLAMA_MODEL` | `llama3` | LLM model name |
| `WHISPER_MODEL` | `base` | tiny/base/small/medium |
| `WAKE_WORD` | `jarvis` | Voice trigger word |
| `TTS_VOICE` | `Samantha` | macOS voice name |
| `SAMPLE_RATE` | `16000` | Mic sample rate |
| `RECORD_SECONDS` | `5` | Max listen window |

---

## 🚨 Troubleshooting

**Ollama not responding:**
```bash
ollama serve   # separate terminal లో run చెయ్యి
```

**Whisper model download slow:**
```bash
# tiny model వాడు (faster, less accurate):
# config.py లో: WHISPER_MODEL = "tiny"
```

**Mic not detected:**
```bash
python3 -c "import sounddevice as sd; print(sd.query_devices())"
# Default input device confirm చెయ్యి
```

**Port 8765 already in use:**
```bash
lsof -i :8765
kill -9 <PID>
```

---

## 🗺️ Roadmap — Next Agents to Build

- [ ] **Calendar Agent** — Google Calendar read/create events
- [ ] **Finance Agent** — Local bank statement parser
- [ ] **Memory Agent** — Long-term conversation memory (ChromaDB)
- [ ] **Security Agent** — Suspicious process monitor

---

*Built for Mac M1 Pro | Llama 3 via Ollama | Whisper STT | Zero API costs*

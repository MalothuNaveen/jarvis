# ============================================================
#  orchestrator/voice.py
#  Local Whisper STT  —  No API key. Runs 100% on M1 Pro.
# ============================================================

import io
import time
import wave
import tempfile
import numpy as np
import sounddevice as sd
import whisper
from rich.console import Console
from config import (
    SAMPLE_RATE, RECORD_SECONDS, SILENCE_THRESHOLD,
    WHISPER_MODEL, WHISPER_LANGUAGE, WAKE_WORD
)

console = Console()

# ── Load Whisper model once at import time ───────────────────
# First run downloads the model (~74 MB for "base") to ~/.cache/whisper
_whisper_model = None

def _get_model():
    global _whisper_model
    if _whisper_model is None:
        console.print(f"[yellow]Loading Whisper '{WHISPER_MODEL}' model...[/yellow]")
        _whisper_model = whisper.load_model(WHISPER_MODEL)
        console.print("[green]Whisper ready.[/green]")
    return _whisper_model


# ── Core: record until silence or max duration ───────────────
def _record_audio(max_seconds: int = RECORD_SECONDS) -> np.ndarray:
    """
    Record from the default mic.
    Stops early when RMS drops below SILENCE_THRESHOLD for 1 second.
    Returns float32 numpy array at SAMPLE_RATE.
    """
    chunk_size  = int(SAMPLE_RATE * 0.5)   # 0.5 s chunks
    max_chunks  = int(max_seconds / 0.5)
    silent_runs = 0
    silent_limit = 2                        # 2 silent chunks (1 s) → stop

    frames = []
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1,
                        dtype="float32", blocksize=chunk_size) as stream:
        for _ in range(max_chunks):
            chunk, _ = stream.read(chunk_size)
            frames.append(chunk)
            rms = np.sqrt(np.mean(chunk ** 2)) * 32768
            if rms < SILENCE_THRESHOLD:
                silent_runs += 1
                if silent_runs >= silent_limit and len(frames) > 4:
                    break
            else:
                silent_runs = 0

    audio = np.concatenate(frames, axis=0).flatten()
    return audio


def _audio_to_text(audio: np.ndarray) -> str:
    """Transcribe numpy float32 audio → text via local Whisper."""
    model  = _get_model()
    result = model.transcribe(
        audio,
        language=WHISPER_LANGUAGE,
        fp16=False          # M1 MPS doesn't need fp16 here
    )
    return result["text"].strip()


# ── Public API ───────────────────────────────────────────────
def listen_once(max_seconds: int = RECORD_SECONDS) -> str:
    """
    Record one utterance and return transcript.
    Use this when you already know the user is speaking.
    """
    console.print("[cyan]🎤 Listening...[/cyan]", end=" ")
    audio = _record_audio(max_seconds)
    text  = _audio_to_text(audio)
    console.print(f"[white]→ '{text}'[/white]")
    return text


def listen_for_wake_word(callback) -> None:
    """
    Continuous loop. When WAKE_WORD is detected in transcript,
    records the full command and calls callback(command_text).

    Usage:
        listen_for_wake_word(lambda cmd: print("Got:", cmd))
    """
    model = _get_model()
    console.print(
        f"[bold green]JARVIS listening for wake word: '{WAKE_WORD}' ...[/bold green]"
    )

    while True:
        try:
            # Short 2-second sample to detect wake word cheaply
            audio = _record_audio(max_seconds=2)
            rms   = np.sqrt(np.mean(audio ** 2)) * 32768
            if rms < SILENCE_THRESHOLD:
                time.sleep(0.1)
                continue

            preview = _audio_to_text(audio).lower()
            if preview:
                console.print(f"[dim]Heard: '{preview}'[/dim]")

            # Check for wake word and phonetic variations
            wake_words = [WAKE_WORD.lower(), "javis", "jarves", "jarv", "garvis", "charvis"]
            if any(w in preview for w in wake_words):
                console.print(f"[bold cyan]⚡ Wake word detected![/bold cyan]")
                
                # Play audio feedback (short modern tick sound)
                import subprocess
                subprocess.run(["afplay", "/System/Library/Sounds/Tink.aiff"])
                
                # Now record the actual command (up to RECORD_SECONDS)
                cmd_audio = _record_audio(max_seconds=RECORD_SECONDS)
                command   = _audio_to_text(cmd_audio)
                
                # Strip the wake words from the command
                command_clean = command.lower()
                for w in wake_words:
                    command_clean = command_clean.replace(w, "")
                command_clean = command_clean.strip()
                
                if command_clean:
                    console.print(f"[bold white]📝 Command: '{command_clean}'[/bold white]")
                    callback(command_clean)
            else:
                time.sleep(0.1)

        except KeyboardInterrupt:
            console.print("\n[red]Voice listener stopped.[/red]")
            break
        except Exception as e:
            console.print(f"[red]Voice error: {e}[/red]")
            time.sleep(1)

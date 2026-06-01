# ============================================================
#  agents/multimedia_agent.py  — Agent 6: Multimedia Creative Agent 🎨🎬
#  Photo/video search & editing using local vision models on M1 NPU
# ============================================================

import os
import glob
from pathlib import Path
from datetime import datetime, timedelta
from .base import BaseAgent
from rich.console import Console

console = Console()

# Common media directories on macOS
PHOTO_DIRS = [
    os.path.expanduser("~/Pictures"),
    os.path.expanduser("~/Desktop"),
    os.path.expanduser("~/Downloads"),
]
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".heic", ".webp", ".gif"}
VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv"}


class MultimediaAgent(BaseAgent):
    agent_id = "multimedia"

    async def execute(self, intent: str, params: dict, raw: str) -> str:
        intent_lower = intent.lower()

        if any(k in intent_lower for k in ["find", "search", "show", "get"]):
            return self._search_media(intent, params)

        if "thumbnail" in intent_lower or "resize" in intent_lower:
            return self._resize_image(params)

        if "screenshot" in intent_lower:
            return self._list_recent_screenshots()

        return f"Multimedia Agent ready. Say 'find photos from last week' to search."

    # ── Search photos/videos ─────────────────────────────────
    def _search_media(self, intent: str, params: dict) -> str:
        """
        Simple date-based file search across PHOTO_DIRS.
        For semantic search (e.g. 'bike photos'), plug in a local
        CLIP model:  pip install transformers torch
        Then encode each image and query against text embedding.
        """
        days = params.get("days", 7)
        cutoff = datetime.now() - timedelta(days=int(days))

        results = []
        for base in PHOTO_DIRS:
            for ext in IMAGE_EXTS | VIDEO_EXTS:
                pattern = os.path.join(base, f"**/*{ext}")
                for f in glob.glob(pattern, recursive=True):
                    mtime = datetime.fromtimestamp(os.path.getmtime(f))
                    if mtime > cutoff:
                        results.append(f)

        if not results:
            return f"No media found in the last {days} days, Boss."

        # Open first 5 in Quick Look
        for f in results[:5]:
            os.system(f'qlmanage -p "{f}" > /dev/null 2>&1 &')

        return (
            f"Found {len(results)} media files from last {days} days. "
            f"Showing first 5 in Quick Look."
        )

    # ── Resize/thumbnail ─────────────────────────────────────
    def _resize_image(self, params: dict) -> str:
        """
        TODO: Use Pillow for real implementation.

        from PIL import Image
        img = Image.open(path)
        img.thumbnail((width, height))
        img.save(output_path)
        """
        path   = params.get("path", "")
        width  = params.get("width", 800)
        height = params.get("height", 600)
        if not path:
            return "Boss, please specify the image path to resize."
        return f"Resize task queued: {path} → {width}x{height}. (Pillow stub)"

    # ── Recent screenshots ────────────────────────────────────
    def _list_recent_screenshots(self) -> str:
        desktop = os.path.expanduser("~/Desktop")
        shots   = sorted(
            glob.glob(os.path.join(desktop, "Screenshot*.png")),
            key=os.path.getmtime, reverse=True
        )[:5]
        if not shots:
            return "No screenshots found on Desktop."
        names = ", ".join(Path(s).name for s in shots)
        return f"Recent screenshots: {names}"

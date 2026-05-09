#!/usr/bin/env python3
"""
Downloads the Moondream2 model from HuggingFace.
Run once before inference.

Usage:
    uv pip install -e .
    python models/download_moondream.py
"""

import sys
from pathlib import Path

MODELS_DIR = Path(__file__).parent
MODEL_DIR = MODELS_DIR / "moondream2"
REPO_ID = "vikhyatk/moondream2"
REVISION = "2025-01-09"


def main() -> None:
    if MODEL_DIR.exists() and any(MODEL_DIR.iterdir()):
        print(f"Already exists: {MODEL_DIR}")
        return

    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        print("Run: uv pip install -e . first")
        sys.exit(1)

    print(f"Downloading Moondream2 ({REPO_ID} @ {REVISION})...")
    snapshot_download(
        repo_id=REPO_ID,
        revision=REVISION,
        local_dir=str(MODEL_DIR),
    )
    print(f"Saved to {MODEL_DIR}")


if __name__ == "__main__":
    main()

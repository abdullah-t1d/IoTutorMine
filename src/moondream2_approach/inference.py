#!/usr/bin/env python3
"""
Runs Moondream2 (via Ollama) on deduplicated frames to extract IoT hardware components.

Pipeline per video:
  1. Load all 1fps frames from data/frames/{video_id}/
  2. pHash deduplication — skip frames too similar to the previous kept frame
  3. Run Moondream2 on each unique frame via Ollama
  4. Aggregate responses → per-video component list

Resumable: already-processed frames are skipped on re-run.

Requirements:
    ollama serve          (must be running)
    ollama pull moondream

Usage:
    python src/moondream2_approach/inference.py
"""

import csv
import sys
from pathlib import Path

import imagehash
import ollama
from PIL import Image

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parents[2]
FRAMES_DIR = ROOT / "data" / "frames"
OUT_DIR = Path(__file__).parent
VLM_RESPONSES_CSV = OUT_DIR / "vlm_responses.csv"
RESULTS_CSV = OUT_DIR / "results.csv"

# ── Config ─────────────────────────────────────────────────────────────────────
MODEL = "moondream"
PHASH_THRESHOLD = 10     # hamming distance; higher = fewer frames kept (0–64)

PROMPT = (
    "List the electronic hardware components you can clearly see in this image. "
    "Be specific (e.g. 'Arduino Uno', 'DHT11 sensor', 'breadboard', 'LED', 'resistor'). "
    "Only include components you are confident about. "
    "If no electronics are visible, respond with 'none'."
)


def check_ollama() -> None:
    try:
        models = [m.model for m in ollama.list().models]
        if not any(MODEL in m for m in models):
            print(f"'{MODEL}' not found. Run: ollama pull {MODEL}")
            sys.exit(1)
    except Exception:
        print("Cannot reach Ollama. Run: ollama serve")
        sys.exit(1)


def select_unique_frames(frame_paths: list[Path]) -> list[Path]:
    """Return frames whose pHash differs enough from the previously kept frame."""
    selected = []
    last_hash = None
    for path in frame_paths:
        try:
            h = imagehash.phash(Image.open(path))
        except Exception:
            continue
        if last_hash is None or (h - last_hash) >= PHASH_THRESHOLD:
            selected.append(path)
            last_hash = h
    return selected


def load_processed_frames() -> set:
    processed = set()
    if not VLM_RESPONSES_CSV.exists():
        return processed
    with open(VLM_RESPONSES_CSV, newline="") as f:
        for row in csv.DictReader(f):
            processed.add((row["video_id"], row["frame"]))
    return processed


def query_frame(image_path: Path) -> str:
    response = ollama.chat(
        model=MODEL,
        messages=[{
            "role": "user",
            "content": PROMPT,
            "images": [str(image_path)],
        }]
    )
    return response["message"]["content"].strip()


def process_video(
    video_id: str,
    processed: set,
    writer,
) -> None:
    frames_dir = FRAMES_DIR / video_id
    all_frames = sorted(frames_dir.glob("*.jpg"))

    if not all_frames:
        print(f"[{video_id}] No frames found, skipping.")
        return

    unique_frames = select_unique_frames(all_frames)
    remaining = [f for f in unique_frames if (video_id, f.name) not in processed]

    if not remaining:
        print(f"[{video_id}] Already processed ({len(unique_frames)} unique frames), skipping.")
        return

    print(
        f"[{video_id}] {len(unique_frames)} unique / {len(all_frames)} total frames "
        f"— {len(remaining)} to process"
    )

    for i, path in enumerate(remaining, 1):
        try:
            response = query_frame(path)
        except Exception as e:
            print(f"  [{video_id}] {path.name} error: {e}", file=sys.stderr)
            response = "error"

        writer.writerow({
            "video_id": video_id,
            "frame": path.name,
            "response": response,
        })
        processed.add((video_id, path.name))

        if i % 10 == 0 or i == len(remaining):
            print(f"  [{video_id}] {i}/{len(remaining)}")

    print(f"[{video_id}] Done.")


def aggregate_results() -> None:
    """Collect all VLM responses per video and write one row per video to results.csv."""
    video_responses: dict[str, list[str]] = {}

    with open(VLM_RESPONSES_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            vid = row["video_id"]
            resp = row["response"].strip().lower()
            if resp and resp != "none" and resp != "error":
                video_responses.setdefault(vid, []).append(row["response"].strip())

    with open(RESULTS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["video_id", "frames_with_components", "all_mentions"])
        writer.writeheader()
        for vid in sorted(video_responses):
            mentions = video_responses[vid]
            writer.writerow({
                "video_id": vid,
                "frames_with_components": len(mentions),
                "all_mentions": " | ".join(mentions),
            })

    print(f"\nResults saved → {RESULTS_CSV.relative_to(ROOT)}")


def main() -> None:
    check_ollama()

    video_ids = sorted(d.name for d in FRAMES_DIR.iterdir() if d.is_dir())
    if not video_ids:
        print(f"No frame directories found in {FRAMES_DIR}")
        sys.exit(1)

    processed = load_processed_frames()

    is_new = not VLM_RESPONSES_CSV.exists()
    with open(VLM_RESPONSES_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["video_id", "frame", "response"])
        if is_new:
            writer.writeheader()

        for video_id in video_ids:
            try:
                process_video(video_id, processed, writer)
                f.flush()
            except Exception as e:
                print(f"[{video_id}] ERROR: {e}", file=sys.stderr)

    aggregate_results()


if __name__ == "__main__":
    main()

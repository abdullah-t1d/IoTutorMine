#!/usr/bin/env python3
"""
MobileCLIP-S2 + pHash deduplication approach for IoT hardware detection.

Pipeline per video:
  1. Load all 1fps frames from data/frames/{video_id}/
  2. pHash deduplication — skip frames too similar to the previous kept frame
  3. Run MobileCLIP-S2 on each unique frame (top-1 component per frame)
  4. Aggregate: keep components that appear in >10% of unique frames

Resumable: already-processed frames are skipped on re-run.

Usage:
    uv run src/mobileclip_phash_approach/inference.py
"""

import csv
import sys
from pathlib import Path

import imagehash
import mobileclip
import torch
from PIL import Image

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parents[2]
FRAMES_DIR = ROOT / "data" / "frames"
MODEL_PATH = ROOT / "models" / "mobileclip_s2.pt"
OUT_DIR = Path(__file__).parent
FRAME_SCORES_CSV = OUT_DIR / "frame_scores.csv"
RESULTS_CSV = OUT_DIR / "results.csv"
SUMMARY_CSV = OUT_DIR / "summary.csv"

# ── Config ─────────────────────────────────────────────────────────────────────
BATCH_SIZE = 32
PHASH_THRESHOLD = 25     # hamming distance cutoff for deduplication (0–64)
FREQ_THRESHOLD = 0.10    # component must appear in >10% of unique frames

# ── Component taxonomy (derived from V01–V10 ground truth + common IoT kit) ────
# Labels are written to be visually descriptive for image-text similarity.
COMPONENTS = [
    # Boards
    "Arduino Uno",
    "Arduino Mega 2560",
    "Raspberry Pi",
    "ESP32",
    "ESP8266",
    # Sensors
    "HC-SR04 ultrasonic sensor",
    "PIR motion sensor",
    "DHT11 sensor",
    "DHT22 sensor",
    "IR sensor",
    "soil moisture sensor",
    "MQ-2 gas sensor",
    # Displays
    "16x2 LCD display",
    "I2C LCD module",
    "OLED display",
    # Passive components
    "LED",
    "resistor",
    "potentiometer",
    "pushbutton",
    "capacitor",
    "buzzer",
    # Prototyping
    "breadboard",
    "jumper wires",
    "USB cable",
    # Actuators & modules
    "servo motor",
    "DC motor",
    "relay module",
    "L298N motor driver",
    "voltage regulator",
]


def load_model():
    print("Loading MobileCLIP-S2...")
    model, _, preprocess = mobileclip.create_model_and_transforms(
        "mobileclip_s2", pretrained=str(MODEL_PATH)
    )
    tokenizer = mobileclip.get_tokenizer("mobileclip_s2")
    model.eval()
    return model, preprocess, tokenizer


def encode_components(model, tokenizer) -> torch.Tensor:
    print(f"Encoding {len(COMPONENTS)} component labels...")
    tokens = tokenizer(COMPONENTS)
    with torch.no_grad():
        text_features = model.encode_text(tokens)
        text_features /= text_features.norm(dim=-1, keepdim=True)
    return text_features


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
    if not FRAME_SCORES_CSV.exists():
        return processed
    with open(FRAME_SCORES_CSV, newline="") as f:
        for row in csv.DictReader(f):
            processed.add((row["video_id"], row["frame"]))
    return processed


def process_video(
    video_id: str,
    model,
    preprocess,
    text_features: torch.Tensor,
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
        f"[{video_id}] {len(unique_frames)} unique / {len(all_frames)} total frames"
        f" — {len(remaining)} to process"
    )

    for i in range(0, len(remaining), BATCH_SIZE):
        batch_paths = remaining[i: i + BATCH_SIZE]
        images, valid_paths = [], []

        for path in batch_paths:
            try:
                img = preprocess(Image.open(path).convert("RGB"))
                images.append(img)
                valid_paths.append(path)
            except Exception as e:
                print(f"  [{video_id}] Skipping {path.name}: {e}", file=sys.stderr)

        if not images:
            continue

        batch = torch.stack(images)
        with torch.no_grad():
            image_features = model.encode_image(batch)
            image_features /= image_features.norm(dim=-1, keepdim=True)

        similarities = image_features @ text_features.T  # (B, num_components)

        for path, scores in zip(valid_paths, similarities):
            top1_idx = scores.argmax().item()
            top1_score = scores[top1_idx].item()
            writer.writerow({
                "video_id": video_id,
                "frame": path.name,
                "component": COMPONENTS[top1_idx],
                "score": round(top1_score, 4),
            })
            processed.add((video_id, path.name))

        if (i // BATCH_SIZE + 1) % 5 == 0 or i + BATCH_SIZE >= len(remaining):
            done = min(i + BATCH_SIZE, len(remaining))
            print(f"  [{video_id}] {done}/{len(remaining)}")

    print(f"[{video_id}] Done.")


def append_video_summary(video_id: str, total_unique: int) -> None:
    """Read frame_scores for this video, apply filters, append one row to summary.csv."""
    component_frames: dict[str, list] = {}
    with open(FRAME_SCORES_CSV, newline="") as f:
        for row in csv.DictReader(f):
            if row["video_id"] != video_id:
                continue
            component_frames.setdefault(row["component"], []).append(row["frame"])

    min_frames = FREQ_THRESHOLD * total_unique
    detected = sorted(
        set(c for c, frames in component_frames.items() if len(frames) >= min_frames),
        key=lambda c: -len(component_frames[c]),
    )

    is_new = not SUMMARY_CSV.exists()
    with open(SUMMARY_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["video_id", "components"])
        if is_new:
            writer.writeheader()
        writer.writerow({
            "video_id": video_id,
            "components": ", ".join(detected) if detected else "none",
        })

    label = ", ".join(detected) if detected else "none"
    print(f"[{video_id}] Summary: {label}")


def aggregate_results() -> None:
    """Count top-1 hits per component per video; keep those above FREQ_THRESHOLD."""
    # Count unique frames processed per video (denominator for frequency)
    video_frame_totals: dict[str, set] = {}
    video_component_frames: dict[str, dict[str, list]] = {}

    with open(FRAME_SCORES_CSV, newline="") as f:
        for row in csv.DictReader(f):
            vid, frame, comp = row["video_id"], row["frame"], row["component"]
            video_frame_totals.setdefault(vid, set()).add(frame)
            video_component_frames.setdefault(vid, {}).setdefault(comp, []).append(frame)

    # We need the total unique frames per video as the denominator,
    # not just frames that had a hit above threshold.
    # Re-read to count ALL processed frames (including those with no hit).
    # Since we only write rows for frames that passed SCORE_THRESHOLD,
    # we use the union of all frames seen in frame_scores as a lower bound.
    # For an accurate denominator, recompute unique frame count per video.
    video_all_unique: dict[str, int] = {}
    for vid in sorted(d.name for d in FRAMES_DIR.iterdir() if d.is_dir()):
        frames_dir = FRAMES_DIR / vid
        all_frames = sorted(frames_dir.glob("*.jpg"))
        if all_frames:
            video_all_unique[vid] = len(select_unique_frames(all_frames))

    with open(RESULTS_CSV, "w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["video_id", "component", "frame_count", "total_unique_frames", "frequency", "frames"]
        )
        writer.writeheader()
        for vid in sorted(video_component_frames):
            total = video_all_unique.get(vid, len(video_frame_totals.get(vid, set())))
            min_frames = FREQ_THRESHOLD * total
            passing = {
                comp: frames
                for comp, frames in video_component_frames[vid].items()
                if len(frames) >= min_frames
            }
            for comp, frames in sorted(passing.items(), key=lambda x: -len(x[1])):
                writer.writerow({
                    "video_id": vid,
                    "component": comp,
                    "frame_count": len(frames),
                    "total_unique_frames": total,
                    "frequency": round(len(frames) / total, 3),
                    "frames": " | ".join(frames),
                })

    print(f"Results saved → {RESULTS_CSV.relative_to(ROOT)}")


def main() -> None:
    if not MODEL_PATH.exists():
        print(f"Model not found at {MODEL_PATH}. Run: python models/download_mobileclip.py")
        sys.exit(1)

    video_ids = sorted(d.name for d in FRAMES_DIR.iterdir() if d.is_dir())
    if not video_ids:
        print(f"No frame directories found in {FRAMES_DIR}")
        sys.exit(1)

    model, preprocess, tokenizer = load_model()
    text_features = encode_components(model, tokenizer)
    processed = load_processed_frames()

    is_new = not FRAME_SCORES_CSV.exists()
    with open(FRAME_SCORES_CSV, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["video_id", "frame", "component", "score"])
        if is_new:
            writer.writeheader()

        for video_id in video_ids:
            try:
                unique_count = len(select_unique_frames(
                    sorted((FRAMES_DIR / video_id).glob("*.jpg"))
                ))
                process_video(video_id, model, preprocess, text_features, processed, writer)
                f.flush()
                append_video_summary(video_id, unique_count)
            except Exception as e:
                print(f"[{video_id}] ERROR: {e}", file=sys.stderr)

    aggregate_results()


if __name__ == "__main__":
    main()

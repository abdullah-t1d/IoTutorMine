#!/usr/bin/env python3
"""
Runs MobileCLIP-S2 on extracted frames and produces a per-video component list.

Resumable: already-processed frames are skipped on re-run.

Usage:
    uv pip install -e .
    python src/mobileclip2_approach/inference.py
"""

import csv
import sys
from pathlib import Path

import torch
from PIL import Image
import mobileclip

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parents[2]
FRAMES_DIR = ROOT / "data" / "frames"
MODEL_PATH = ROOT / "models" / "mobileclip_s2.pt"
OUT_DIR = Path(__file__).parent
FRAME_SCORES_CSV = OUT_DIR / "frame_scores.csv"
RESULTS_CSV = OUT_DIR / "results.csv"

# ── Config ─────────────────────────────────────────────────────────────────────
BATCH_SIZE = 32
TOP_K = 5            # top-k components scored per frame
SCORE_THRESHOLD = 0.20   # min cosine similarity to record
FREQ_THRESHOLD = 0.05    # component must appear in >5% of frames to make final list

# ── Component taxonomy ─────────────────────────────────────────────────────────
COMPONENTS = [
    # Boards
    "Arduino Uno microcontroller board",
    "Arduino Mega microcontroller board",
    "Raspberry Pi single board computer",
    "ESP32 microcontroller",
    "ESP8266 WiFi module",
    # Sensors
    "HC-SR04 ultrasonic distance sensor",
    "DHT11 temperature and humidity sensor",
    "DHT22 temperature and humidity sensor",
    "HC-SR501 PIR motion sensor",
    "water level sensor module",
    "IR infrared sensor",
    "soil moisture sensor",
    # Displays
    "16x2 LCD character display",
    "I2C LCD display module",
    "OLED display module",
    "Waveshare touchscreen LCD",
    # Communication
    "RC522 RFID reader module",
    "RFID card or tag",
    "Bluetooth HC-05 module",
    "PiicoDev RFID module",
    # Actuators
    "servo motor",
    "DC motor",
    "piezo buzzer",
    "relay module",
    # Passive components
    "LED",
    "resistor",
    "capacitor",
    "potentiometer",
    # Other
    "breadboard",
    "jumper wires",
    "USB cable",
    "GPIO pins",
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
    print(f"Encoding {len(COMPONENTS)} components...")
    tokens = tokenizer(COMPONENTS)
    with torch.no_grad():
        text_features = model.encode_text(tokens)
        text_features /= text_features.norm(dim=-1, keepdim=True)
    return text_features


def load_processed_frames() -> set:
    """Returns set of (video_id, frame_name) already written to frame_scores.csv."""
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

    remaining = [f for f in all_frames if (video_id, f.name) not in processed]
    if not remaining:
        print(f"[{video_id}] Already fully processed ({len(all_frames)} frames), skipping.")
        return

    print(f"[{video_id}] {len(remaining)}/{len(all_frames)} frames to process...")

    for i in range(0, len(remaining), BATCH_SIZE):
        batch_paths = remaining[i : i + BATCH_SIZE]
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
            top_indices = scores.topk(TOP_K).indices.tolist()
            for idx in top_indices:
                score = scores[idx].item()
                if score >= SCORE_THRESHOLD:
                    writer.writerow({
                        "video_id": video_id,
                        "frame": path.name,
                        "component": COMPONENTS[idx],
                        "score": round(score, 4),
                    })
            processed.add((video_id, path.name))

    print(f"[{video_id}] Done.")


def aggregate_results() -> None:
    """Reads frame_scores.csv and writes the final per-video component list to results.csv."""
    video_frames: dict = {}
    video_counts: dict = {}

    with open(FRAME_SCORES_CSV, newline="") as f:
        for row in csv.DictReader(f):
            vid, frame, comp = row["video_id"], row["frame"], row["component"]
            video_frames.setdefault(vid, set()).add(frame)
            video_counts.setdefault(vid, {})
            video_counts[vid][comp] = video_counts[vid].get(comp, 0) + 1

    with open(RESULTS_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["video_id", "components", "component_count"])
        writer.writeheader()
        for vid in sorted(video_counts):
            total = len(video_frames[vid])
            min_frames = FREQ_THRESHOLD * total
            detected = sorted(
                [c for c, n in video_counts[vid].items() if n >= min_frames],
                key=lambda c: video_counts[vid][c],
                reverse=True,
            )
            writer.writerow({
                "video_id": vid,
                "components": " | ".join(detected),
                "component_count": len(detected),
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
                process_video(video_id, model, preprocess, text_features, processed, writer)
                f.flush()  # persist to disk after each video
            except Exception as e:
                print(f"[{video_id}] ERROR: {e}", file=sys.stderr)

    aggregate_results()


if __name__ == "__main__":
    main()

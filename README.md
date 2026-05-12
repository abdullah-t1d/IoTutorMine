# IoTutorMine-Web

A web tool that extracts hardware Bills of Materials (BoMs) from IoT tutorial videos using Large Language Models.

**Live tool:** https://ahmedbahaj.github.io/IoTutorMine/

**Paper:** *IoTutorMine: A Tool for Mining Hardware Bills of Materials from IoT Tutorial Videos*, ASE 2026 Tools and Datasets Track.

## What it does

IoTutorMine helps IoT learners answer "what hardware do I need?" before following a YouTube tutorial. The tool indexes IoT tutorials and exposes their parts lists as searchable tags.

## How it works

1. Fetch the YouTube auto-generated transcript
2. Clean and prepare it
3. Send it to an LLM with a structured prompt that returns a deduplicated table of components

The library currently contains 20 tutorials (Arduino + Raspberry Pi, beginner + intermediate).

## Authors

- Abdullah A. Alahmadi — University of Jeddah
- Ahmed O. Bahaj — University of Jeddah
- Mohammad D. Alahmadi — University of Jeddah

## License

MIT License. See [LICENSE](LICENSE).

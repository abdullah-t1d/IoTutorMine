const ALLOWED_ORIGINS = [
  "https://ahmedbahaj.github.io",
  "https://abdullah-t1d.github.io",
  "http://localhost:5173"
];

const MODEL = "gemini-3-flash-preview";

const PROMPT = `You extract a hardware Bill of Materials from an IoT tutorial transcript.
Return every shoppable hardware component the presenter mentions or uses.
Rules:
- Only physically purchasable hardware parts.
- Exclude integrated parts, consumables, software, and parts mentioned only for context or contrast.
- Label each as "USED" or "ALTERNATIVE".
- Deduplicate. Use the most specific name stated.
Return ONLY JSON in exactly this shape:
{"components":[{"name":"...","status":"USED"}]}

Transcript:
`;

function setCors(req, res) {
  const origin = req.headers.origin;
  const allowOrigin = ALLOWED_ORIGINS.includes(origin)
    ? origin
    : "https://ahmedbahaj.github.io";

  res.setHeader("Access-Control-Allow-Origin", allowOrigin);
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
}

function parseId(url) {
  const m = String(url || "").match(/(?:v=|youtu\.be\/|embed\/|shorts\/)([\w-]{11})/);
  return m ? m[1] : null;
}

async function getTranscript(videoId) {
  // 1) Try direct YouTube timedtext endpoints first
  const directUrls = [
    `https://www.youtube.com/api/timedtext?v=${videoId}&lang=en&fmt=json3`,
    `https://www.youtube.com/api/timedtext?v=${videoId}&lang=en&kind=asr&fmt=json3`,
    `https://video.google.com/timedtext?v=${videoId}&lang=en&fmt=json3`,
    `https://video.google.com/timedtext?v=${videoId}&lang=en&kind=asr&fmt=json3`
  ];

  for (const u of directUrls) {
    const text = await transcriptFromJson3(u);
    if (text) return text;
  }

  // 2) Fallback: parse captionTracks from YouTube watch page
  const pageRes = await fetch(`https://www.youtube.com/watch?v=${videoId}`, {
    headers: {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
      "Accept-Language": "en-US,en;q=0.9"
    }
  });

  const page = await pageRes.text();

  // YouTube often escapes JSON inside HTML, so normalize common escapes
  const normalized = page
    .replace(/\\"/g, '"')
    .replace(/\\u0026/g, "&")
    .replace(/\\\//g, "/");

  const m = normalized.match(/"captionTracks":(\[.*?\])/);
  if (!m) return null;

  let tracks;
  try {
    tracks = JSON.parse(m[1]);
  } catch {
    return null;
  }

  if (!tracks.length) return null;

  const track =
    tracks.find(t => t.languageCode === "en" && t.kind !== "asr") ||
    tracks.find(t => t.languageCode === "en") ||
    tracks[0];

  if (!track?.baseUrl) return null;

  const text = await transcriptFromJson3(track.baseUrl + "&fmt=json3");
  return text || null;
}

async function transcriptFromJson3(url) {
  try {
    const res = await fetch(url, {
      headers: {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9"
      }
    });

    const raw = await res.text();
    if (!raw || raw.trim().startsWith("<")) return null;

    const data = JSON.parse(raw);

    const text = (data.events || [])
      .flatMap(ev => (ev.segs || []).map(s => s.utf8 || ""))
      .join(" ")
      .replace(/\s+/g, " ")
      .trim()
      .toLowerCase();

    return text || null;
  } catch {
    return null;
  }
}

async function callGemini(transcript, key) {
  const endpoint = `https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent`;

  const geminiRes = await fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-goog-api-key": key
    },
    body: JSON.stringify({
      contents: [{ parts: [{ text: PROMPT + transcript }] }],
      generationConfig: {
        responseMimeType: "application/json"
      }
    })
  });

  const data = await geminiRes.json();

  if (!geminiRes.ok) {
    throw new Error(data?.error?.message || "Gemini request failed");
  }

  const raw = data?.candidates?.[0]?.content?.parts?.[0]?.text || "{}";

  try {
    return JSON.parse(raw).components || [];
  } catch {
    return [];
  }
}

function cleanTranscript(text) {
  return String(text || "")
    .replace(/\s+/g, " ")
    .trim()
    .toLowerCase();
}

export default async function handler(req, res) {
  setCors(req, res);

  if (req.method === "OPTIONS") {
    return res.status(204).end();
  }

  if (req.method !== "POST") {
    return res.status(405).json({ error: "POST only" });
  }

  try {
    const { url, transcript } = req.body || {};

    let videoId = parseId(url);
    let finalTranscript = cleanTranscript(transcript);

    // If no manual transcript is provided, try YouTube URL extraction
    if (!finalTranscript) {
      if (!videoId) {
        return res.status(400).json({
          error: "Provide either a valid YouTube URL or a transcript."
        });
      }

      finalTranscript = await getTranscript(videoId);

      if (!finalTranscript) {
        return res.status(422).json({
          error: "No transcript available for this video. You can paste the transcript manually."
        });
      }
    }

    const components = await callGemini(finalTranscript, process.env.GEMINI_KEY);

    return res.status(200).json({
      videoId: videoId || null,
      source: transcript ? "manual-transcript" : "youtube-url",
      components
    });
  } catch (e) {
    return res.status(500).json({
      error: e.message || "Extraction failed"
    });
  }
}

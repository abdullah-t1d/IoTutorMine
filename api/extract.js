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
  const pageRes = await fetch(`https://www.youtube.com/watch?v=${videoId}`, {
    headers: {
      "User-Agent": "Mozilla/5.0",
      "Accept-Language": "en-US,en;q=0.9"
    }
  });

  const page = await pageRes.text();
  const m = page.match(/"captionTracks":(\[.*?\])/);
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

  const transcriptRes = await fetch(track.baseUrl + "&fmt=json3");
  const data = await transcriptRes.json();

  const text = (data.events || [])
    .flatMap(ev => (ev.segs || []).map(s => s.utf8 || ""))
    .join(" ")
    .replace(/\s+/g, " ")
    .trim()
    .toLowerCase();

  return text || null;
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

export default async function handler(req, res) {
  setCors(req, res);

  if (req.method === "OPTIONS") {
    return res.status(204).end();
  }

  if (req.method !== "POST") {
    return res.status(405).json({ error: "POST only" });
  }

  try {
    const { url } = req.body || {};
    const videoId = parseId(url);

    if (!videoId) {
      return res.status(400).json({ error: "Invalid YouTube URL" });
    }

    const transcript = await getTranscript(videoId);

    if (!transcript) {
      return res.status(422).json({ error: "No transcript available for this video" });
    }

    const components = await callGemini(transcript, process.env.GEMINI_KEY);

    return res.status(200).json({
      videoId,
      components
    });
  } catch (e) {
    return res.status(500).json({
      error: e.message || "Extraction failed"
    });
  }
}

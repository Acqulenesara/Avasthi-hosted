const DIET_API_URL = process.env.REACT_APP_DIET_API_URL || "";

/** Fire-and-forget ping — just wakes the diet server, doesn't block anything */
export function wakeDietServer() {
  if (!DIET_API_URL) return;
  fetch(`${DIET_API_URL}/`, { method: "GET" }).catch(() => {});
}

export async function recommendDiet(profile, attempt = 1) {
  if (!DIET_API_URL) {
    throw new Error(
      "Diet service URL is not configured. Please set REACT_APP_DIET_API_URL in your Vercel environment variables."
    );
  }

  const controller = new AbortController();
  // 60s per attempt — Render cold start + TF model load can take ~40s
  const timeoutId = setTimeout(() => controller.abort(), 60000);

  try {
    const res = await fetch(`${DIET_API_URL}/diet/recommend`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...profile, top_n: 5 }),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!res.ok) {
      const err = await res.text();
      throw new Error(`Diet API error ${res.status}: ${err}`);
    }

    return res.json();
  } catch (err) {
    clearTimeout(timeoutId);
    if (err.message.includes("not configured")) throw err; // don't retry config errors
    if (attempt < 4) {
      // retry up to 3 more times with increasing wait
      await new Promise((r) => setTimeout(r, attempt * 5000));
      return recommendDiet(profile, attempt + 1);
    }
    if (err.name === "AbortError") {
      throw new Error("Diet server is taking too long. Please try again in a moment.");
    }
    throw err;
  }
}

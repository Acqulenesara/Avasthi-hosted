export async function recommendDiet(profile) {
  const baseUrl =
    process.env.REACT_APP_API_URL ||
    "http://127.0.0.1:8000";

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 90000);

  try {
    const res = await fetch(`${baseUrl}/diet/recommend`, {
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
    if (err.name === "AbortError") {
      throw new Error("Request timed out. The server may be waking up — please try again in a moment.");
    }
    throw err;
  }
}

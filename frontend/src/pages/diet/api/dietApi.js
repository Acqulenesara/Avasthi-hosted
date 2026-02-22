const DIET_API_URL =
  process.env.REACT_APP_DIET_API_URL ||
  process.env.REACT_APP_API_URL ||
  "http://127.0.0.1:8000";

/** Wake-up ping so the diet service is warm before the user hits "Get Meal Plan" */
export async function wakeDietServer() {
  for (let i = 0; i < 6; i++) {
    try {
      const res = await fetch(`${DIET_API_URL}/`, { method: "GET" });
      if (res.ok) return true;
    } catch (_) {
      /* still cold */
    }
    await new Promise((r) => setTimeout(r, 5000));
  }
  return false; // best-effort — let the user try anyway
}

export async function recommendDiet(profile, attempt = 1) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 90000);

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
    if (attempt < 3) {
      await new Promise((r) => setTimeout(r, 5000));
      return recommendDiet(profile, attempt + 1);
    }
    if (err.name === "AbortError") {
      throw new Error("Request timed out after 3 attempts. The diet server may be waking up — please try again.");
    }
    throw err;
  }
}

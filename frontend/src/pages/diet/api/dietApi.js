export async function recommendDiet(profile) {
  const baseUrl =
    process.env.REACT_APP_DIET_API_URL ||
    process.env.REACT_APP_API_URL ||
    "http://127.0.0.1:8001";
  const res = await fetch(
    `${baseUrl}/diet/recommend`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...profile, top_n: 5 }),
    }
  );

  if (!res.ok) {
    const err = await res.text();
    throw new Error(`Diet API error ${res.status}: ${err}`);
  }

  return res.json();
}

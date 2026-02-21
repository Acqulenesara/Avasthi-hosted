export async function recommendDiet(profile) {
  const res = await fetch("http://127.0.0.1:8001/diet-recommend", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...profile, top_n: 5 }),
  });

  return res.json();
}

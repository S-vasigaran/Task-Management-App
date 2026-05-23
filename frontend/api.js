const API_BASE = "";

async function api(path, method = "GET", body = null, token = null) {
  const headers = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(API_BASE + path, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (res.status === 204) return null;

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    const detail = data.detail;
    if (typeof detail === "string") throw new Error(detail);
    if (Array.isArray(detail))
      throw new Error(detail.map((d) => d.msg).join(", "));
    throw new Error("Something went wrong");
  }

  return data;
}

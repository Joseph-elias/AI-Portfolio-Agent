export type SourceItem = { source: string; snippet: string };
export type ChatHistoryTurn = { role: "assistant" | "user"; content: string };

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function postChat(message: string, language: "en" | "fr", history: ChatHistoryTurn[] = []) {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, language, history })
  });
  return res.json();
}

export async function postJobFit(job_description: string, language: "en" | "fr") {
  const res = await fetch(`${API_BASE}/job-fit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ job_description, language })
  });
  return res.json();
}

export async function getProfileSummary() {
  const res = await fetch(`${API_BASE}/profile-summary`);
  return res.json();
}
"use client";

import { useEffect, useMemo, useRef, useState, type KeyboardEvent } from "react";
import { postChat, type ChatHistoryTurn } from "@/lib/api";
import SampleQuestions from "@/components/SampleQuestions";

type Props = { language: "en" | "fr" };

type ChatMessage = {
  id: string;
  role: "assistant" | "user";
  text: string;
};

function createGreeting(language: "en" | "fr"): ChatMessage {
  return {
    id: "greeting",
    role: "assistant",
    text:
      language === "fr"
        ? "Bonjour, je suis Agent Joseph. Posez-moi vos questions sur mon profil, mes projets ou une offre d emploi. Je reponds avec des preuves claires."
        : "Hi, I am Agent Joseph. Ask me about my profile, projects, or a job post. I respond with clear evidence."
  };
}

function cleanAssistantText(text: string): string {
  return text
    .replace(/^#{1,6}\s+/gm, "")
    .replace(/^(Evidence-grounded summary:|Resume base sur les preuves disponibles:|Summary:|Result:|Resultat:)\s*/gim, "")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

export default function ChatBox({ language }: Props) {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([createGreeting(language)]);
  const [loading, setLoading] = useState(false);
  const listRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setMessages([createGreeting(language)]);
    setMessage("");
  }, [language]);

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  const sendLabel = useMemo(() => (language === "fr" ? "Envoyer" : "Send"), [language]);

  async function submit() {
    const trimmed = message.trim();
    if (!trimmed || loading) return;

    const userMessage: ChatMessage = { id: `u_${Date.now()}`, role: "user", text: trimmed };
    const nextMessages = [...messages, userMessage];
    setMessages(nextMessages);
    setMessage("");
    setLoading(true);

    const history: ChatHistoryTurn[] = nextMessages
      .filter((m) => m.id !== "greeting")
      .slice(-8)
      .map((m) => ({ role: m.role, content: m.text }));

    try {
      const data = await postChat(trimmed, language, history);

      const assistantMessage: ChatMessage = {
        id: `a_${Date.now()}`,
        role: "assistant",
        text: cleanAssistantText(
          data.answer || (language === "fr" ? "Je n ai pas trouve de reponse fiable." : "I could not find a reliable answer.")
        )
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } finally {
      setLoading(false);
    }
  }

  function onKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      void submit();
    }
  }

  const lastAssistant = [...messages].reverse().find((m) => m.role === "assistant")?.text || "";

  return (
    <div className="grid gap-5 xl:grid-cols-[minmax(0,1.45fr)_minmax(290px,0.82fr)]">
      <section className="section-shell hero-shell p-4 md:p-5">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-2xl font-semibold">{language === "fr" ? "Parlez avec Joseph" : "Talk with Joseph"}</h2>
          </div>
          <span className="soft-tag text-xs font-semibold uppercase tracking-[0.22em]">{language === "fr" ? "en ligne" : "online"}</span>
        </div>

        <div
          ref={listRef}
          className="chat-scroll max-h-[60vh] overflow-y-auto rounded-[32px] border border-[rgba(31,35,64,0.08)] bg-[rgba(255,252,248,0.7)] p-4 md:max-h-[560px] md:p-5"
        >
          <div className="space-y-3">
            {messages.map((m) => (
              <div key={m.id} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                <div className={`message-fade-in max-w-[90%] overflow-visible ${m.role === "user" ? "chat-bubble-user" : "chat-bubble-assistant"}`}>
                  {m.role === "assistant" && (
                    <p className="mb-1 text-[11px] font-semibold uppercase tracking-[0.24em] text-[var(--muted)]">Agent Joseph</p>
                  )}
                  <p className="whitespace-pre-wrap break-words text-[15px] leading-7">{m.text}</p>
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex justify-start">
                <div className="chat-bubble-assistant max-w-[70%]">
                  <p className="mb-1 text-[11px] font-semibold uppercase tracking-[0.24em] text-[var(--muted)]">Agent Joseph</p>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-[var(--muted)]">{language === "fr" ? "Reflexion" : "Thinking"}</span>
                    <span className="typing-dot" />
                    <span className="typing-dot" />
                    <span className="typing-dot" />
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="mt-4 section-shell blob-card bg-[rgba(255,251,246,0.8)] p-4">
          <textarea
            className="form-field h-28 resize-none rounded-[26px] px-4 py-3 text-[15px] leading-7"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={onKeyDown}
            placeholder={
              language === "fr"
                ? "Ecrivez votre message... (Entree pour envoyer, Shift+Entree pour nouvelle ligne)"
                : "Write your message... (Enter to send, Shift+Enter for new line)"
            }
          />
          <div className="mt-4 flex flex-wrap gap-3">
            <button className="pill-button pill-primary text-sm" onClick={submit} disabled={loading}>
              {loading ? "..." : sendLabel}
            </button>
            <button
              className="pill-button pill-secondary text-sm"
              onClick={() => navigator.clipboard.writeText(lastAssistant)}
              type="button"
            >
              {language === "fr" ? "Copier la derniere reponse" : "Copy latest reply"}
            </button>
          </div>
        </div>
      </section>

      <aside className="space-y-5">
        <SampleQuestions language={language} onPick={setMessage} />
      </aside>
    </div>
  );
}


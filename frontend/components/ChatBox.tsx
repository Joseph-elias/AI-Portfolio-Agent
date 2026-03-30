"use client";

import { useEffect, useMemo, useRef, useState, type KeyboardEvent } from "react";
import { postChat, SourceItem, type ChatHistoryTurn } from "@/lib/api";
import SourceList from "@/components/SourceList";
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
  const [sources, setSources] = useState<SourceItem[]>([]);
  const [loading, setLoading] = useState(false);
  const listRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setMessages([createGreeting(language)]);
    setSources([]);
    setMessage("");
  }, [language]);

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  const sendLabel = useMemo(() => (language === "fr" ? "Envoyer" : "Send"), [language]);

  async function submit() {
    const trimmed = message.trim();
    if (!trimmed) return;

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
      setSources(data.sources || []);

      const assistantMessage: ChatMessage = {
        id: `a_${Date.now()}`,
        role: "assistant",
        text: cleanAssistantText(
          data.answer || (language === "fr" ? "Je n ai pas trouve de reponse fiable." : "I could not find a reliable answer.")
        ),
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
    <div className="grid gap-5 md:grid-cols-3">
      <div className="md:col-span-2 space-y-3">
        <section className="tech-panel rounded-3xl p-4 md:p-5">
          <div className="mb-3 flex items-center justify-between">
            <p className="code-chip text-[11px] uppercase tracking-[0.22em] text-ink/55">
              {language === "fr" ? "conversation live" : "live conversation"}
            </p>
            <span className="rounded-full bg-emerald-100 px-3 py-1 text-[11px] font-semibold text-emerald-700">
              {language === "fr" ? "En ligne" : "Online"}
            </span>
          </div>

          <div ref={listRef} className="chat-scroll max-h-[520px] space-y-3 overflow-y-auto rounded-2xl border border-ink/10 bg-white/95 p-4">
            {messages.map((m) => (
              <div key={m.id} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                <div className={`message-fade-in max-w-[88%] ${m.role === "user" ? "chat-bubble-user" : "chat-bubble-assistant"}`}>
                  {m.role === "assistant" && (
                    <p className="mb-1 text-[11px] font-semibold uppercase tracking-wide text-ink/55">Agent Joseph</p>
                  )}
                  <p className="whitespace-pre-wrap text-[15px] leading-7">{m.text}</p>
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex justify-start">
                <div className="chat-bubble-assistant max-w-[70%]">
                  <p className="mb-1 text-[11px] font-semibold uppercase tracking-wide text-ink/55">Agent Joseph</p>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-ink/70">{language === "fr" ? "Reflexion" : "Thinking"}</span>
                    <span className="typing-dot" />
                    <span className="typing-dot" />
                    <span className="typing-dot" />
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="mt-4 rounded-2xl border border-ink/10 bg-white p-3">
            <textarea
              className="h-24 w-full resize-none rounded-xl border border-ink/15 bg-slatebase/50 p-3 text-[15px] leading-6 outline-none transition focus:border-accent/50"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={onKeyDown}
              placeholder={
                language === "fr"
                  ? "Ecrivez votre message... (Entree pour envoyer, Shift+Entree pour nouvelle ligne)"
                  : "Write your message... (Enter to send, Shift+Enter for new line)"
              }
            />
            <div className="mt-3 flex flex-wrap gap-2">
              <button className="rounded-xl bg-accent px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:brightness-110" onClick={submit}>
                {loading ? "..." : sendLabel}
              </button>
              <button className="rounded-xl border border-ink/15 bg-white px-4 py-2.5 text-sm" onClick={() => navigator.clipboard.writeText(lastAssistant)}>
                {language === "fr" ? "Copier la derniere reponse" : "Copy latest reply"}
              </button>
            </div>
          </div>
        </section>
      </div>

      <aside className="space-y-4">
        <SampleQuestions language={language} onPick={setMessage} />
        <SourceList sources={sources} language={language} />
      </aside>
    </div>
  );
}

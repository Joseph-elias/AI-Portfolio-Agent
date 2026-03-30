"use client";

import Link from "next/link";
import ChatBox from "@/components/ChatBox";
import LanguageToggle from "@/components/LanguageToggle";
import BrandIdentity from "@/components/BrandIdentity";
import { useAppLanguage, withLanguage } from "@/lib/language";

export default function ChatPage() {
  const { language, setLanguage } = useAppLanguage("en");

  return (
    <main className="mx-auto max-w-6xl space-y-6 p-6 md:p-10">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <BrandIdentity compact language={language} />
          <LanguageToggle language={language} setLanguage={setLanguage} />
        </div>
        <Link href={withLanguage("/", language)} className="code-chip rounded-lg border border-ink/25 bg-white px-3 py-2 text-xs uppercase tracking-wide">
          {language === "fr" ? "Retour accueil" : "Back Home"}
        </Link>
      </div>

      <section className="tech-panel rounded-2xl p-5 md:p-6">
        <p className="code-chip mb-2 text-xs uppercase tracking-[0.2em] text-ink/60">mode_01</p>
        <h1 className="text-3xl font-bold md:text-4xl">{language === "fr" ? "Chat avec Joseph" : "Chat with Joseph"}</h1>
        <p className="mt-2 text-sm text-ink/75">
          {language === "fr"
            ? "Experience conversationnelle: posez vos questions comme dans une vraie discussion."
            : "Conversational experience: ask questions as if you were talking directly with me."}
        </p>
      </section>

      <ChatBox language={language} />
    </main>
  );
}

"use client";

import Link from "next/link";
import ChatBox from "@/components/ChatBox";
import LanguageToggle from "@/components/LanguageToggle";
import BrandIdentity from "@/components/BrandIdentity";
import { useAppLanguage, withLanguage } from "@/lib/language";

export default function ChatPage() {
  const { language, setLanguage } = useAppLanguage("en");

  return (
    <main className="app-shell mx-auto max-w-6xl px-5 py-6 md:px-8 md:py-10">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <BrandIdentity compact language={language} />
        <div className="flex flex-wrap items-center gap-3">
          <LanguageToggle language={language} setLanguage={setLanguage} />
          <Link href={withLanguage("/", language)} className="pill-button pill-secondary code-chip text-xs uppercase tracking-[0.22em]">
            {language === "fr" ? "Retour accueil" : "Back home"}
          </Link>
        </div>
      </div>

      <section className="section-shell hero-shell mt-6 p-6 md:p-8">
        <h1 className="display-title mt-4 text-4xl font-semibold md:text-6xl">
          {language === "fr" ? "Conversation" : "Conversation"} <span className="gradient-text">chat</span>
        </h1>
      </section>

      <div className="mt-6">
        <ChatBox language={language} />
      </div>
    </main>
  );
}

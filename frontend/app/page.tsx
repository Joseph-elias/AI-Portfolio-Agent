"use client";

import Link from "next/link";
import LanguageToggle from "@/components/LanguageToggle";
import BrandIdentity from "@/components/BrandIdentity";
import { useAppLanguage, withLanguage } from "@/lib/language";

const copy = {
  en: {
    subtitle: "Talk with me through a bilingual AI profile assistant built for recruiters.",
    badges: ["Bilingual RAG", "Source-Cited", "Recruiter Mode"],
    askTitle: "Chat With Joseph",
    askText: "Conversational assistant backed by your real portfolio data.",
    fitTitle: "Analyze a Job",
    fitText: "Fit score, strengths, gaps, and positioning suggestions.",
    aboutTitle: "Links and Profile",
    aboutText: "Resume, GitHub, LinkedIn, and contact details."
  },
  fr: {
    subtitle: "Discutez avec moi via un assistant IA bilingue concu pour les recruteurs.",
    badges: ["RAG Bilingue", "Reponses Sourcees", "Mode Recruteur"],
    askTitle: "Discuter avec Joseph",
    askText: "Assistant conversationnel base sur les vraies donnees du portfolio.",
    fitTitle: "Analyser une offre",
    fitText: "Score de fit, points forts, ecarts et recommandations.",
    aboutTitle: "Liens et profil",
    aboutText: "CV, GitHub, LinkedIn et informations de contact."
  }
} as const;

export default function HomePage() {
  const { language, setLanguage } = useAppLanguage("en");
  const t = copy[language];

  return (
    <main className="relative mx-auto max-w-6xl p-6 md:p-10">
      <header className="tech-panel mb-8 rounded-2xl p-6 md:p-8">
        <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-4">
            <BrandIdentity language={language} />
            <LanguageToggle language={language} setLanguage={setLanguage} />
          </div>
          <div className="flex flex-wrap gap-2">
            {t.badges.map((badge) => (
              <span key={badge} className="code-chip rounded-full border border-ink/20 bg-white px-3 py-1 text-xs text-ink/80">
                {badge}
              </span>
            ))}
          </div>
        </div>

        <h1 className="mb-3 text-4xl font-bold tracking-tight md:text-5xl">AI Portfolio Agent</h1>
        <p className="max-w-3xl text-base text-ink/80 md:text-lg">{t.subtitle}</p>
      </header>

      <section className="grid gap-4 md:grid-cols-3">
        <Link href={withLanguage("/chat", language)} className="tech-panel group rounded-2xl p-5 transition hover:-translate-y-0.5 hover:border-accent/50">
          <p className="code-chip mb-2 text-xs uppercase tracking-[0.2em] text-ink/60">mode_01</p>
          <h2 className="mb-2 text-xl font-semibold">{t.askTitle}</h2>
          <p className="text-sm text-ink/75">{t.askText}</p>
        </Link>
        <Link href={withLanguage("/job-fit", language)} className="tech-panel group rounded-2xl p-5 transition hover:-translate-y-0.5 hover:border-accent/50">
          <p className="code-chip mb-2 text-xs uppercase tracking-[0.2em] text-ink/60">mode_02</p>
          <h2 className="mb-2 text-xl font-semibold">{t.fitTitle}</h2>
          <p className="text-sm text-ink/75">{t.fitText}</p>
        </Link>
        <Link href={withLanguage("/about", language)} className="tech-panel group rounded-2xl p-5 transition hover:-translate-y-0.5 hover:border-accent/50">
          <p className="code-chip mb-2 text-xs uppercase tracking-[0.2em] text-ink/60">mode_03</p>
          <h2 className="mb-2 text-xl font-semibold">{t.aboutTitle}</h2>
          <p className="text-sm text-ink/75">{t.aboutText}</p>
        </Link>
      </section>
    </main>
  );
}

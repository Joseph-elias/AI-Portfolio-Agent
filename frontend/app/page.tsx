"use client";

import Link from "next/link";
import LanguageToggle from "@/components/LanguageToggle";
import BrandIdentity from "@/components/BrandIdentity";
import { useAppLanguage, withLanguage } from "@/lib/language";

const copy = {
  en: {
    eyebrow: "AI portfolio experience",
    askTitle: "Chat the profile",
    askText: "Start a conversation around projects, strengths, and technical decisions.",
    fitTitle: "Read a job fit",
    fitText: "Paste a role and get a precise fit analysis with strengths and gaps.",
    aboutTitle: "Open the profile",
    aboutText: "Browse links, resume access, and the key signals a recruiter needs fast.",
    heroStatA: "AI + product thinking",
    heroStatB: "Backend and RAG depth",
    heroStatC: "Bilingual recruiter flow"
  },
  fr: {
    eyebrow: "experience portfolio IA",
    askTitle: "Discuter avec le profil",
    askText: "Lancer une conversation sur les projets, les points forts et les choix techniques.",
    fitTitle: "Lire un job fit",
    fitText: "Coller une offre et obtenir une analyse precise avec points forts et ecarts.",
    aboutTitle: "Ouvrir le profil",
    aboutText: "Parcourir les liens, les CV et les signaux clefs pour recruteurs.",
    heroStatA: "IA + vision produit",
    heroStatB: "Profondeur backend et RAG",
    heroStatC: "Parcours bilingue recruteur"
  }
} as const;

const cardShapes = ["blob-card", "blob-card-alt", "blob-card"];

export default function HomePage() {
  const { language, setLanguage } = useAppLanguage("en");
  const t = copy[language];

  const cards = [
    { href: withLanguage("/chat", language), title: t.askTitle, text: t.askText },
    { href: withLanguage("/job-fit", language), title: t.fitTitle, text: t.fitText },
    { href: withLanguage("/about", language), title: t.aboutTitle, text: t.aboutText }
  ];

  return (
    <main className="app-shell mx-auto max-w-6xl px-5 py-6 md:px-8 md:py-10">
      <section className="section-shell hero-shell float-in p-6 md:p-8 lg:p-10">
        <div className="absolute -right-12 top-10 h-44 w-44 rounded-full bg-[rgba(93,167,160,0.14)] blur-2xl" />
        <div className="absolute bottom-0 left-10 h-32 w-32 rounded-full bg-[rgba(222,108,75,0.14)] blur-2xl" />

        <div className="relative flex flex-wrap items-start justify-between gap-4">
          <div className="space-y-6">
            <div className="flex flex-wrap items-center gap-3">
              <BrandIdentity language={language} />
              <div className="soft-tag text-xs">{t.eyebrow}</div>
            </div>
            <div className="max-w-3xl">
              <h1 className="display-title mt-2 text-5xl font-semibold md:text-7xl">
                Joseph&apos;s <span className="gradient-text">AI portfolio</span>
              </h1>
            </div>
          </div>
          <LanguageToggle language={language} setLanguage={setLanguage} />
        </div>

        <div className="relative mt-8 grid gap-4 md:grid-cols-3">
          {[t.heroStatA, t.heroStatB, t.heroStatC].map((stat, index) => (
            <div key={stat} className={`section-shell ${index === 1 ? "blob-card-alt" : "blob-card"} bg-[rgba(255,251,246,0.78)] p-4`}>
              <p className="mt-3 text-sm font-medium leading-6">{stat}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="mt-6 grid gap-4 md:grid-cols-3">
        {cards.map((card, index) => (
          <Link
            key={card.href}
            href={card.href}
            className={`section-shell ${cardShapes[index]} float-in-delayed group min-h-[220px] p-6 transition duration-200 hover:-translate-y-1`}
          >
            <div className="flex h-full flex-col justify-between gap-6">
              <div>
                <h2 className="mt-4 text-2xl font-semibold">{card.title}</h2>
                <p className="mt-3 text-sm leading-7 text-[var(--muted)]">{card.text}</p>
              </div>
              <div className="flex items-center justify-between">
                <span className="pill-button pill-secondary text-sm">{language === "fr" ? "Explorer" : "Explore"}</span>
                <span className="text-2xl text-[var(--accent)] transition group-hover:translate-x-1">↗</span>
              </div>
            </div>
          </Link>
        ))}
      </section>
    </main>
  );
}

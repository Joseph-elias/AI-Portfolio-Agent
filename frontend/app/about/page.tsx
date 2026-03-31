"use client";

import Link from "next/link";
import LanguageToggle from "@/components/LanguageToggle";
import BrandIdentity from "@/components/BrandIdentity";
import { useAppLanguage, withLanguage } from "@/lib/language";

const links = {
  en: [
    { label: "Resume (EN)", href: "/resume_en.pdf" },
    { label: "Resume (FR)", href: "/resume_fr.pdf" },
    { label: "GitHub", href: "https://github.com/joseph-elias" },
    { label: "LinkedIn", href: "https://www.linkedin.com/in/joseph-elias-al-khoury-0a54a8239/" },
    { label: "Technical portfolio", href: "https://joseph-elias.github.io/Portfolio-joseph/" }
  ],
  fr: [
    { label: "CV (anglais)", href: "/resume_en.pdf" },
    { label: "CV (francais)", href: "/resume_fr.pdf" },
    { label: "GitHub", href: "https://github.com/joseph-elias" },
    { label: "LinkedIn", href: "https://www.linkedin.com/in/joseph-elias-al-khoury-0a54a8239/" },
    { label: "Portfolio technique", href: "https://joseph-elias.github.io/Portfolio-joseph/" }
  ]
} as const;

export default function AboutPage() {
  const { language, setLanguage } = useAppLanguage("en");
  const items = links[language];

  return (
    <main className="app-shell mx-auto max-w-5xl px-5 py-6 md:px-8 md:py-10">
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
          {language === "fr" ? "Profil" : "Profile"} <span className="gradient-text">links</span>
        </h1>
        <p className="mt-4 max-w-2xl text-base leading-8 text-[var(--muted)] md:text-lg">
          {language === "fr"
            ? "Retrouvez ici tous les liens utiles."
            : "Find all useful profile links here."}
        </p>
      </section>

      <section className="mt-6 grid gap-4 md:grid-cols-2">
        {items.map((item, index) => (
          <a
            key={item.label}
            className={`section-shell ${index % 2 === 0 ? "blob-card" : "blob-card-alt"} p-5 transition duration-200 hover:-translate-y-1`}
            href={item.href}
            target={item.href.startsWith("http") || item.href.endsWith(".pdf") ? "_blank" : undefined}
            rel={item.href.startsWith("http") || item.href.endsWith(".pdf") ? "noreferrer" : undefined}
          >
            <div className="mt-4 flex items-start justify-between gap-3">
              <div>
                <h2 className="text-2xl font-semibold">{item.label}</h2>
              </div>
              <span className="text-2xl text-[var(--accent)]">↗</span>
            </div>
          </a>
        ))}
      </section>
    </main>
  );
}

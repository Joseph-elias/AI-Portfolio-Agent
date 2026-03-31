"use client";

import Link from "next/link";
import LanguageToggle from "@/components/LanguageToggle";
import BrandIdentity from "@/components/BrandIdentity";
import { useAppLanguage, withLanguage } from "@/lib/language";

const links = {
  en: [
    { label: "Resume (EN)", href: "#", tone: "Warm positioning summary for English-speaking recruiters." },
    { label: "Resume (FR)", href: "#", tone: "French version for local academic or hiring contexts." },
    { label: "GitHub", href: "https://github.com/joseph-elias", tone: "Code, repositories, and implementation range." },
    { label: "LinkedIn", href: "https://www.linkedin.com/", tone: "Professional profile and career narrative." },
    { label: "Technical portfolio", href: "https://joseph-elias.github.io/Portfolio-joseph/", tone: "A broader portfolio view beyond the assistant." }
  ],
  fr: [
    { label: "CV (anglais)", href: "#", tone: "Version positionnee pour recruteurs internationaux." },
    { label: "CV (francais)", href: "#", tone: "Version adaptee au contexte local ou academique." },
    { label: "GitHub", href: "https://github.com/joseph-elias", tone: "Code, depots et amplitude technique." },
    { label: "LinkedIn", href: "https://www.linkedin.com/", tone: "Profil professionnel et trajectoire." },
    { label: "Portfolio technique", href: "https://joseph-elias.github.io/Portfolio-joseph/", tone: "Vue plus large du travail au-dela de l assistant." }
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
        <p className="code-chip text-[11px] uppercase tracking-[0.3em] text-[var(--muted)]/75">flow_03</p>
        <h1 className="display-title mt-4 text-4xl font-semibold md:text-6xl">
          {language === "fr" ? "Profil" : "Profile"} <span className="gradient-text">access</span>
        </h1>
        <p className="mt-4 max-w-2xl text-base leading-8 text-[var(--muted)] md:text-lg">
          {language === "fr"
            ? "Tous les liens importants dans une presentation plus douce et plus editoriale, avec une lecture rapide pour recruteurs et partenaires."
            : "All key links in a softer, more editorial presentation designed for quick recruiter and partner review."}
        </p>
      </section>

      <section className="mt-6 grid gap-4 md:grid-cols-2">
        {items.map((item, index) => (
          <a
            key={item.label}
            className={`section-shell ${index % 2 === 0 ? "blob-card" : "blob-card-alt"} p-5 transition duration-200 hover:-translate-y-1`}
            href={item.href}
            target={item.href.startsWith("http") ? "_blank" : undefined}
            rel={item.href.startsWith("http") ? "noreferrer" : undefined}
          >
            <p className="code-chip text-[11px] uppercase tracking-[0.28em] text-[var(--muted)]/75">link_0{index + 1}</p>
            <div className="mt-4 flex items-start justify-between gap-3">
              <div>
                <h2 className="text-2xl font-semibold">{item.label}</h2>
                <p className="mt-3 text-sm leading-7 text-[var(--muted)]">{item.tone}</p>
              </div>
              <span className="text-2xl text-[var(--accent)]">↗</span>
            </div>
          </a>
        ))}
      </section>
    </main>
  );
}

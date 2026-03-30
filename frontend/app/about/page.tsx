"use client";

import Link from "next/link";
import LanguageToggle from "@/components/LanguageToggle";
import { useAppLanguage, withLanguage } from "@/lib/language";

export default function AboutPage() {
  const { language, setLanguage } = useAppLanguage("en");

  return (
    <main className="mx-auto max-w-4xl space-y-6 p-6 md:p-10">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <LanguageToggle language={language} setLanguage={setLanguage} />
        <Link href={withLanguage("/", language)} className="code-chip rounded-lg border border-ink/25 bg-white px-3 py-2 text-xs uppercase tracking-wide">
          {language === "fr" ? "Retour accueil" : "Back Home"}
        </Link>
      </div>

      <section className="tech-panel space-y-3 rounded-2xl p-6">
        <p className="code-chip text-xs uppercase tracking-[0.2em] text-ink/60">mode_03</p>
        <h1 className="text-3xl font-bold md:text-4xl">{language === "fr" ? "Liens et profil" : "About and Links"}</h1>
        <p className="text-ink/80">
          {language === "fr"
            ? "References rapides pour les recruteurs et contacts utiles."
            : "Recruiter-friendly references and contact links."}
        </p>
      </section>

      <ul className="grid gap-3 text-sm md:grid-cols-2">
        <li className="tech-panel rounded-xl p-4"><a className="text-accent underline" href="#">{language === "fr" ? "CV (anglais)" : "Resume (EN)"}</a></li>
        <li className="tech-panel rounded-xl p-4"><a className="text-accent underline" href="#">{language === "fr" ? "CV (francais)" : "Resume (FR)"}</a></li>
        <li className="tech-panel rounded-xl p-4"><a className="text-accent underline" href="https://github.com/joseph-elias" target="_blank" rel="noreferrer">GitHub</a></li>
        <li className="tech-panel rounded-xl p-4"><a className="text-accent underline" href="https://www.linkedin.com/" target="_blank" rel="noreferrer">LinkedIn</a></li>
        <li className="tech-panel rounded-xl p-4 md:col-span-2"><a className="text-accent underline" href="https://joseph-elias.github.io/Portfolio-joseph/" target="_blank" rel="noreferrer">{language === "fr" ? "Portfolio technique" : "Technical portfolio"}</a></li>
      </ul>
    </main>
  );
}

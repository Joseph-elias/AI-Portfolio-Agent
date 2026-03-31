"use client";

import Link from "next/link";
import { useState } from "react";
import LanguageToggle from "@/components/LanguageToggle";
import FitScoreCard from "@/components/FitScoreCard";
import SourceList from "@/components/SourceList";
import BrandIdentity from "@/components/BrandIdentity";
import { postJobFit, SourceItem } from "@/lib/api";
import { useAppLanguage, withLanguage } from "@/lib/language";

type JobFitResult = {
  fit_score: number;
  fit_label: string;
  summary: string;
  matched_skills: string[];
  missing_skills: string[];
  relevant_projects: string[];
  sources: SourceItem[];
};

export default function JobFitPage() {
  const { language, setLanguage } = useAppLanguage("en");
  const [jd, setJd] = useState("");
  const [result, setResult] = useState<JobFitResult | null>(null);
  const [loading, setLoading] = useState(false);

  async function analyze() {
    if (!jd.trim() || loading) return;
    setLoading(true);
    try {
      const data = await postJobFit(jd, language);
      setResult(data);
    } finally {
      setLoading(false);
    }
  }

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
        <div className="grid gap-5 md:grid-cols-[1.25fr_0.85fr] md:items-end">
          <div>
            <p className="code-chip text-[11px] uppercase tracking-[0.3em] text-[var(--muted)]/75">flow_02</p>
            <h1 className="display-title mt-4 text-4xl font-semibold md:text-6xl">
              {language === "fr" ? "Lecture" : "Role"} <span className="gradient-text">job fit</span>
            </h1>
            <p className="mt-4 max-w-2xl text-base leading-8 text-[var(--muted)] md:text-lg">
              {language === "fr"
                ? "Collez une offre pour obtenir une lecture visuelle et argumentee du match entre le poste et le profil de Joseph."
                : "Paste a role to get a visual, evidence-based read on how Joseph matches the position."}
            </p>
          </div>
          <div className="section-shell blob-card-alt bg-[linear-gradient(135deg,rgba(255,248,241,0.92),rgba(255,232,220,0.8))] p-5">
            <p className="text-sm leading-7 text-[var(--muted)]">
              {language === "fr"
                ? "Le resultat est pense comme une note de positionnement: score, resume, competences alignees, manques et projets les plus convaincants."
                : "The result is shaped like a positioning note: score, summary, aligned skills, gaps, and the strongest supporting projects."}
            </p>
          </div>
        </div>
      </section>

      <section className="section-shell blob-card mt-6 p-5 md:p-6">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="code-chip text-[11px] uppercase tracking-[0.28em] text-[var(--muted)]/80">
              {language === "fr" ? "brief de poste" : "role brief"}
            </p>
            <h2 className="mt-2 text-2xl font-semibold">{language === "fr" ? "Analyser une offre" : "Analyze a job description"}</h2>
          </div>
          <button className="pill-button pill-primary text-sm" onClick={analyze}>
            {loading ? "..." : language === "fr" ? "Analyser" : "Analyze"}
          </button>
        </div>
        <textarea
          className="form-field h-64 rounded-[30px] px-4 py-4 text-sm leading-7"
          value={jd}
          onChange={(e) => setJd(e.target.value)}
          placeholder={language === "fr" ? "Collez l offre d emploi ici..." : "Paste the job description here..."}
        />
      </section>

      {result && (
        <section className="mt-6 grid gap-5 lg:grid-cols-[320px_minmax(0,1fr)]">
          <FitScoreCard score={result.fit_score} label={result.fit_label} language={language} />
          <div className="space-y-5">
            <div className="section-shell blob-card-alt p-6">
              <p className="code-chip text-[11px] uppercase tracking-[0.28em] text-[var(--muted)]/80">
                {language === "fr" ? "synthese" : "summary"}
              </p>
              <p className="mt-4 text-sm leading-7 text-[var(--muted)]">{result.summary}</p>
              <div className="aurora-divider my-5" />
              <div className="grid gap-4 md:grid-cols-3">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--muted)]">
                    {language === "fr" ? "Competences alignees" : "Matched skills"}
                  </p>
                  <p className="mt-2 text-sm leading-7">{(result.matched_skills || []).join(", ") || "-"}</p>
                </div>
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--muted)]">
                    {language === "fr" ? "Competences manquantes" : "Missing skills"}
                  </p>
                  <p className="mt-2 text-sm leading-7">{(result.missing_skills || []).join(", ") || "-"}</p>
                </div>
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--muted)]">
                    {language === "fr" ? "Projets pertinents" : "Relevant projects"}
                  </p>
                  <p className="mt-2 text-sm leading-7">{(result.relevant_projects || []).join(", ") || "-"}</p>
                </div>
              </div>
            </div>
            <SourceList sources={result.sources || []} language={language} />
          </div>
        </section>
      )}
    </main>
  );
}

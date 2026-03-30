"use client";

import Link from "next/link";
import { useState } from "react";
import LanguageToggle from "@/components/LanguageToggle";
import FitScoreCard from "@/components/FitScoreCard";
import SourceList from "@/components/SourceList";
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
    if (!jd.trim()) return;
    setLoading(true);
    const data = await postJobFit(jd, language);
    setResult(data);
    setLoading(false);
  }

  return (
    <main className="mx-auto max-w-6xl space-y-6 p-6 md:p-10">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <LanguageToggle language={language} setLanguage={setLanguage} />
        <Link href={withLanguage("/", language)} className="code-chip rounded-lg border border-ink/25 bg-white px-3 py-2 text-xs uppercase tracking-wide">
          {language === "fr" ? "Retour accueil" : "Back Home"}
        </Link>
      </div>

      <section className="tech-panel rounded-2xl p-5 md:p-6">
        <p className="code-chip mb-2 text-xs uppercase tracking-[0.2em] text-ink/60">mode_02</p>
        <h1 className="text-3xl font-bold md:text-4xl">{language === "fr" ? "Analyse d adequation poste" : "Job Fit Analyzer"}</h1>
      </section>

      <section className="tech-panel space-y-4 rounded-2xl p-5 md:p-6">
        <textarea
          className="h-56 w-full rounded-xl border border-ink/20 bg-white p-3 text-sm"
          value={jd}
          onChange={(e) => setJd(e.target.value)}
          placeholder={language === "fr" ? "Collez l offre d emploi ici..." : "Paste the job description here..."}
        />
        <button className="rounded-lg bg-accent px-5 py-2 text-white" onClick={analyze}>
          {loading ? "..." : language === "fr" ? "Analyser" : "Analyze"}
        </button>
      </section>

      {result && (
        <section className="grid gap-4 md:grid-cols-3">
          <FitScoreCard score={result.fit_score} label={result.fit_label} language={language} />
          <div className="tech-panel rounded-2xl p-4 md:col-span-2">
            <p className="code-chip mb-2 text-xs uppercase tracking-[0.2em] text-ink/60">{language === "fr" ? "resume" : "summary"}</p>
            <p className="text-sm leading-6">{result.summary}</p>
            <p className="mt-3 text-sm">
              <strong>{language === "fr" ? "Competences alignees" : "Matched skills"}:</strong> {(result.matched_skills || []).join(", ") || "-"}
            </p>
            <p className="text-sm">
              <strong>{language === "fr" ? "Competences manquantes" : "Missing skills"}:</strong> {(result.missing_skills || []).join(", ") || "-"}
            </p>
            <p className="text-sm">
              <strong>{language === "fr" ? "Projets pertinents" : "Relevant projects"}:</strong> {(result.relevant_projects || []).join(", ") || "-"}
            </p>
          </div>
          <div className="md:col-span-3">
            <SourceList sources={result.sources || []} language={language} />
          </div>
        </section>
      )}
    </main>
  );
}

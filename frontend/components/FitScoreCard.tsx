export default function FitScoreCard({ score, label, language }: { score: number; label: string; language: "en" | "fr" }) {
  return (
    <div className="tech-panel rounded-2xl p-4">
      <p className="code-chip text-xs uppercase tracking-[0.2em] text-ink/60">{language === "fr" ? "score_fit" : "fit_score"}</p>
      <p className="mt-2 text-4xl font-bold text-accent">{score}/100</p>
      <p className="mt-2 text-sm">{label}</p>
    </div>
  );
}

import { SourceItem } from "@/lib/api";

export default function SourceList({ sources, language }: { sources: SourceItem[]; language: "en" | "fr" }) {
  return (
    <div className="section-shell blob-card-alt p-5">
      <div className="mb-4 flex items-center justify-between gap-3">
        <div>
          <p className="code-chip text-[11px] uppercase tracking-[0.28em] text-[var(--muted)]/80">sources</p>
          <h3 className="mt-2 text-lg font-semibold">{language === "fr" ? "Preuves utilisees" : "Evidence used"}</h3>
        </div>
        <div className="h-10 w-10 rounded-full bg-[rgba(222,108,75,0.14)]" />
      </div>
      {sources.length === 0 ? (
        <p className="text-sm leading-6 text-[var(--muted)]">
          {language === "fr" ? "Les sources apparaitront ici apres la premiere reponse." : "Sources will appear here after the first response."}
        </p>
      ) : (
        <ul className="space-y-3 text-sm">
          {sources.map((s, idx) => (
            <li
              key={`${s.source}-${idx}`}
              className="rounded-[24px] border border-[rgba(31,35,64,0.08)] bg-[rgba(255,251,246,0.9)] p-4 shadow-[0_12px_24px_rgba(31,35,64,0.05)]"
            >
              <p className="mb-1 font-semibold text-[var(--ink)]">{s.source}</p>
              <p className="leading-6 text-[var(--muted)]">{s.snippet}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

import { SourceItem } from "@/lib/api";

export default function SourceList({ sources, language }: { sources: SourceItem[]; language: "en" | "fr" }) {
  return (
    <div className="tech-panel rounded-2xl p-4">
      <h3 className="code-chip mb-3 text-xs uppercase tracking-[0.2em] text-ink/60">
        {language === "fr" ? "sources" : "sources"}
      </h3>
      {sources.length === 0 ? (
        <p className="text-sm text-ink/65">{language === "fr" ? "Aucune source a afficher." : "No sources to display yet."}</p>
      ) : (
        <ul className="space-y-2 text-sm">
          {sources.map((s, idx) => (
            <li key={`${s.source}-${idx}`} className="rounded-lg border border-ink/15 bg-white p-3">
              <p className="mb-1 font-semibold">{s.source}</p>
              <p className="text-ink/80">{s.snippet}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

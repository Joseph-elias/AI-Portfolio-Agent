export default function SampleQuestions({ language, onPick }: { language: "en" | "fr"; onPick: (q: string) => void }) {
  const en = [
    "What makes his AI profile stand out for a product team?",
    "Which projects best prove his backend engineering depth?",
    "How does he combine RAG, APIs, and delivery?"
  ];
  const fr = [
    "Qu est-ce qui rend son profil IA fort pour une equipe produit ?",
    "Quels projets prouvent le mieux sa profondeur backend ?",
    "Comment combine-t-il RAG, APIs et execution ?"
  ];
  const questions = language === "fr" ? fr : en;

  return (
    <div className="section-shell blob-card p-5">
      <div className="mb-4 flex items-center justify-between gap-3">
        <div>
          <h3 className="mt-2 text-lg font-semibold">{language === "fr" ? "Questions rapides" : "Quick starters"}</h3>
        </div>
        <div className="h-10 w-10 rounded-full bg-[rgba(93,167,160,0.16)]" />
      </div>
      <div className="space-y-3">
        {questions.map((q) => (
          <button
            key={q}
            className="w-full rounded-[24px] border border-[rgba(31,35,64,0.08)] bg-[rgba(255,251,246,0.88)] px-4 py-3 text-left text-sm leading-6 text-[var(--ink)] transition hover:-translate-y-0.5 hover:border-[rgba(222,108,75,0.24)] hover:shadow-[0_16px_30px_rgba(31,35,64,0.08)]"
            onClick={() => onPick(q)}
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  );
}

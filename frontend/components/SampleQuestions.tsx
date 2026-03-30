export default function SampleQuestions({ language, onPick }: { language: "en" | "fr"; onPick: (q: string) => void }) {
  const en = [
    "What are his top AI engineering strengths?",
    "Does he have experience with RAG systems?",
    "Which projects best show backend skills?"
  ];
  const fr = [
    "Quels sont ses meilleurs points forts en IA ?",
    "A-t-il deja construit des systemes RAG ?",
    "Quels projets montrent le mieux ses competences backend ?"
  ];
  const questions = language === "fr" ? fr : en;

  return (
    <div className="tech-panel rounded-2xl p-4">
      <p className="code-chip mb-3 text-xs uppercase tracking-[0.2em] text-ink/60">
        {language === "fr" ? "questions_exemple" : "sample_questions"}
      </p>
      <div className="space-y-2">
        {questions.map((q) => (
          <button
            key={q}
            className="block w-full rounded-lg border border-ink/20 bg-white p-2 text-left text-sm transition hover:border-accent/50"
            onClick={() => onPick(q)}
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  );
}

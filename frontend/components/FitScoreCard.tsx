export default function FitScoreCard({ score, label, language }: { score: number; label: string; language: "en" | "fr" }) {
  const circumference = 2 * Math.PI * 52;
  const progress = circumference - (Math.max(0, Math.min(score, 100)) / 100) * circumference;

  return (
    <div className="section-shell blob-card p-6">
      <p className="code-chip text-[11px] uppercase tracking-[0.28em] text-[var(--muted)]/80">
        {language === "fr" ? "lecture du fit" : "fit reading"}
      </p>
      <div className="mt-6 flex items-center justify-center">
        <div className="relative grid h-40 w-40 place-items-center rounded-full bg-[radial-gradient(circle,_rgba(255,255,255,0.9)_0%,_rgba(255,244,238,0.9)_70%)] shadow-[0_24px_40px_rgba(31,35,64,0.08)]">
          <svg viewBox="0 0 120 120" className="absolute inset-0 h-full w-full -rotate-90">
            <circle cx="60" cy="60" r="52" fill="none" stroke="rgba(31,35,64,0.08)" strokeWidth="8" />
            <circle
              cx="60"
              cy="60"
              r="52"
              fill="none"
              stroke="url(#fitGradient)"
              strokeLinecap="round"
              strokeWidth="8"
              strokeDasharray={circumference}
              strokeDashoffset={progress}
            />
            <defs>
              <linearGradient id="fitGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#de6c4b" />
                <stop offset="100%" stopColor="#5da7a0" />
              </linearGradient>
            </defs>
          </svg>
          <div className="text-center">
            <p className="text-4xl font-bold gradient-text">{score}</p>
            <p className="mt-1 text-xs uppercase tracking-[0.24em] text-[var(--muted)]">/ 100</p>
          </div>
        </div>
      </div>
      <p className="mt-6 text-center text-sm leading-6 text-[var(--muted)]">{label}</p>
    </div>
  );
}

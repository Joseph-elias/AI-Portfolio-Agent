"use client";

type Props = {
  language: "en" | "fr";
  setLanguage: (value: "en" | "fr") => void;
};

export default function LanguageToggle({ language, setLanguage }: Props) {
  return (
    <div className="section-shell inline-flex items-center gap-1 rounded-full border-white/50 bg-white/60 p-1.5 shadow-sm">
      <button
        className={`rounded-full px-4 py-2 text-xs font-semibold tracking-[0.2em] transition ${
          language === "en" ? "bg-[var(--ink)] text-white shadow-sm" : "text-[var(--muted)]"
        }`}
        onClick={() => setLanguage("en")}
      >
        EN
      </button>
      <button
        className={`rounded-full px-4 py-2 text-xs font-semibold tracking-[0.2em] transition ${
          language === "fr" ? "bg-[var(--ink)] text-white shadow-sm" : "text-[var(--muted)]"
        }`}
        onClick={() => setLanguage("fr")}
      >
        FR
      </button>
    </div>
  );
}

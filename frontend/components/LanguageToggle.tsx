"use client";

type Props = {
  language: "en" | "fr";
  setLanguage: (value: "en" | "fr") => void;
};

export default function LanguageToggle({ language, setLanguage }: Props) {
  return (
    <div className="inline-flex items-center gap-2 rounded-full border border-ink/20 bg-white p-1 shadow-sm">
      <button
        className={`rounded-full px-4 py-1 text-xs font-semibold tracking-wide ${
          language === "en" ? "bg-accent text-white" : "text-ink/80"
        }`}
        onClick={() => setLanguage("en")}
      >
        EN
      </button>
      <button
        className={`rounded-full px-4 py-1 text-xs font-semibold tracking-wide ${
          language === "fr" ? "bg-accent text-white" : "text-ink/80"
        }`}
        onClick={() => setLanguage("fr")}
      >
        FR
      </button>
    </div>
  );
}

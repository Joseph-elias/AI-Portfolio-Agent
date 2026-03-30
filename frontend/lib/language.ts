"use client";

import { useEffect, useState } from "react";

export type Language = "en" | "fr";

const STORAGE_KEY = "ai_portfolio_agent_language";

function normalizeLanguage(value: string | null): Language {
  return value === "fr" ? "fr" : "en";
}

export function useAppLanguage(defaultLanguage: Language = "en") {
  const [language, setLanguageState] = useState<Language>(defaultLanguage);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const urlLanguage = normalizeLanguage(params.get("lang"));
    const storedLanguage = normalizeLanguage(window.localStorage.getItem(STORAGE_KEY));

    if (params.get("lang")) {
      setLanguageState(urlLanguage);
      window.localStorage.setItem(STORAGE_KEY, urlLanguage);
      return;
    }

    setLanguageState(storedLanguage);
  }, []);

  useEffect(() => {
    document.documentElement.lang = language;
  }, [language]);

  function setLanguage(nextLanguage: Language) {
    setLanguageState(nextLanguage);
    window.localStorage.setItem(STORAGE_KEY, nextLanguage);
  }

  return { language, setLanguage };
}

export function withLanguage(path: string, language: Language): string {
  return `${path}?lang=${language}`;
}

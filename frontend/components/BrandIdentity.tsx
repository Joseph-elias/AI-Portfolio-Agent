import Image from "next/image";

type Props = {
  compact?: boolean;
  language: "en" | "fr";
};

export default function BrandIdentity({ compact = false, language }: Props) {
  return (
    <div className="flex items-center gap-4">
      <div
        className={`section-shell relative overflow-hidden border border-white/50 bg-white/55 ${
          compact ? "h-14 w-14 rounded-[28px]" : "h-16 w-16 rounded-[32px]"
        }`}
      >
        <div className="absolute inset-0 bg-gradient-to-br from-white/50 via-transparent to-[rgba(222,108,75,0.2)]" />
        <Image src="/profile.JPG" alt="Joseph avatar" fill className="object-cover" priority />
      </div>
      <div>
        <p className="text-lg font-semibold leading-none md:text-xl">Joseph AI</p>
        <p className="mt-1 text-sm text-[var(--muted)]">
          {language === "fr" ? "assistant portfolio concu pour recruteurs" : "portfolio assistant shaped for recruiters"}
        </p>
      </div>
    </div>
  );
}

import Image from "next/image";

type Props = {
  compact?: boolean;
  language: "en" | "fr";
};

export default function BrandIdentity({ compact = false, language }: Props) {
  return (
    <div className="flex items-center gap-3">
      <div className={`relative overflow-hidden rounded-2xl border border-ink/25 bg-white ${compact ? "h-11 w-11" : "h-14 w-14"}`}>
        <Image
          src="/profile.JPG"
          alt="Joseph avatar"
          fill
          className="object-cover"
          priority
        />
      </div>
      <div>
        <p className="text-lg font-semibold leading-none">Joseph AI</p>
        <p className="code-chip mt-1 text-xs uppercase tracking-wide text-ink/65">
          {language === "fr" ? "assistant portfolio en ligne" : "live portfolio assistant"}
        </p>
      </div>
    </div>
  );
}


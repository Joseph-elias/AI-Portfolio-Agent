import argparse
import time
from dataclasses import dataclass


@dataclass
class BenchmarkCase:
    name: str
    en_question: str
    fr_question: str
    en_tokens: list[str]
    fr_tokens: list[str]


CASES = [
    BenchmarkCase(
        name="self_intro",
        en_question="Introduce yourself in 3 lines.",
        fr_question="Presente-toi en 3 lignes.",
        en_tokens=["ai engineer", "sissi", "institut curie"],
        fr_tokens=["ingenieur ia", "sissi", "institut curie"],
    ),
    BenchmarkCase(
        name="experience",
        en_question="What professional experience do you have?",
        fr_question="Quelle experience professionnelle as-tu ?",
        en_tokens=["sissi", "institut curie"],
        fr_tokens=["sissi", "institut curie"],
    ),
    BenchmarkCase(
        name="internship",
        en_question="Do you have internship and alternance experience?",
        fr_question="As-tu une experience de stage et d alternance ?",
        en_tokens=["m1", "m2", "institut curie"],
        fr_tokens=["m1", "m2", "institut curie"],
    ),
    BenchmarkCase(
        name="education",
        en_question="What is your education background?",
        fr_question="Quel est ton parcours d etudes ?",
        en_tokens=["master", "bachelor"],
        fr_tokens=["master", "licence"],
    ),
    BenchmarkCase(
        name="contracts",
        en_question="What contract types are you looking for?",
        fr_question="Quels types de contrats recherches-tu ?",
        en_tokens=["cdi", "cdd"],
        fr_tokens=["cdi", "cdd"],
    ),
    BenchmarkCase(
        name="skills_rag",
        en_question="Do you have experience with RAG?",
        fr_question="As-tu de l experience avec le RAG ?",
        en_tokens=["yes", "rag"],
        fr_tokens=["oui", "rag"],
    ),
    BenchmarkCase(
        name="skills_fastapi",
        en_question="Have you used FastAPI?",
        fr_question="As-tu utilise FastAPI ?",
        en_tokens=["yes", "fastapi"],
        fr_tokens=["oui", "fastapi"],
    ),
    BenchmarkCase(
        name="publication",
        en_question="Do you have a publication from Curie work?",
        fr_question="As-tu une publication issue des travaux a Curie ?",
        en_tokens=["manuscript", "lifex"],
        fr_tokens=["manuscrit", "lifex"],
    ),
    BenchmarkCase(
        name="hire",
        en_question="Why should we hire you for an AI engineer role?",
        fr_question="Pourquoi te recruter pour un role d ingenieur IA ?",
        en_tokens=["backend", "deploy"],
        fr_tokens=["backend", "deploy"],
    ),
    BenchmarkCase(
        name="languages",
        en_question="Which languages do you work in?",
        fr_question="Quelles langues parles-tu ?",
        en_tokens=["english", "french", "arabic"],
        fr_tokens=["anglais", "francais", "arabe"],
    ),
]


def _score_answer(answer: str, tokens: list[str]) -> tuple[int, int, bool]:
    low = (answer or "").lower()
    hits = sum(1 for t in tokens if t in low)
    needed = max(1, (len(tokens) + 1) // 2)
    return hits, needed, hits >= needed


def _build_client(api_url: str | None):
    if api_url:
        import httpx

        client = httpx.Client(base_url=api_url.rstrip("/"), timeout=60)

        def ask(message: str, language: str) -> tuple[str, float]:
            t0 = time.perf_counter()
            r = client.post("/chat", json={"message": message, "language": language, "history": []})
            dt = time.perf_counter() - t0
            data = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
            return str(data.get("answer", "")), dt

        return ask

    from fastapi.testclient import TestClient
    from app.main import app

    tc = TestClient(app)

    def ask(message: str, language: str) -> tuple[str, float]:
        t0 = time.perf_counter()
        r = tc.post("/chat", json={"message": message, "language": language, "history": []})
        dt = time.perf_counter() - t0
        data = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
        return str(data.get("answer", "")), dt

    return ask


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark EN vs FR chat quality.")
    parser.add_argument("--api-url", default=None, help="Optional deployed backend URL, e.g. https://...onrender.com")
    args = parser.parse_args()

    ask = _build_client(args.api_url)

    en_pass = 0
    fr_pass = 0
    parity_pass = 0
    en_total_t = 0.0
    fr_total_t = 0.0

    print("name,en_pass,fr_pass,en_hits/en_need,fr_hits/fr_need,en_time_s,fr_time_s")
    for case in CASES:
        en_answer, en_t = ask(case.en_question, "en")
        fr_answer, fr_t = ask(case.fr_question, "fr")

        en_hits, en_need, en_ok = _score_answer(en_answer, case.en_tokens)
        fr_hits, fr_need, fr_ok = _score_answer(fr_answer, case.fr_tokens)

        en_pass += int(en_ok)
        fr_pass += int(fr_ok)
        parity_pass += int(en_ok and fr_ok)
        en_total_t += en_t
        fr_total_t += fr_t

        print(f"{case.name},{int(en_ok)},{int(fr_ok)},{en_hits}/{en_need},{fr_hits}/{fr_need},{en_t:.2f},{fr_t:.2f}")

    n = len(CASES)
    print("\n=== Summary ===")
    print(f"EN pass rate: {en_pass}/{n} ({(100*en_pass/n):.1f}%)")
    print(f"FR pass rate: {fr_pass}/{n} ({(100*fr_pass/n):.1f}%)")
    print(f"EN-FR parity pass: {parity_pass}/{n} ({(100*parity_pass/n):.1f}%)")
    print(f"Avg EN latency: {en_total_t/n:.2f}s")
    print(f"Avg FR latency: {fr_total_t/n:.2f}s")


if __name__ == "__main__":
    main()

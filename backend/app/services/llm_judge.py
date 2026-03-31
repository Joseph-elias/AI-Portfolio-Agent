from __future__ import annotations

import json
import re
from dataclasses import dataclass

from ..core.config import ENABLE_LLM_JUDGE, OPENAI_API_KEY, OPENAI_CHAT_MODEL, USE_OPENAI

try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None


@dataclass
class JudgeResult:
    checked: bool
    passed: bool
    revised_answer: str | None = None
    notes: str = ""


class LLMJudge:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=OPENAI_API_KEY) if (ENABLE_LLM_JUDGE and USE_OPENAI and OpenAI is not None) else None

    @property
    def enabled(self) -> bool:
        return self.client is not None

    @staticmethod
    def _extract_json(text: str) -> dict | None:
        payload = text.strip()
        try:
            obj = json.loads(payload)
            return obj if isinstance(obj, dict) else None
        except Exception:
            pass

        m = re.search(r"\{.*\}", payload, flags=re.DOTALL)
        if not m:
            return None
        try:
            obj = json.loads(m.group(0))
            return obj if isinstance(obj, dict) else None
        except Exception:
            return None

    def review(
        self,
        *,
        message: str,
        answer: str,
        language: str,
        plan_intent: str,
        required_keywords: list[str],
        sources_context: str,
    ) -> JudgeResult:
        if not self.enabled:
            return JudgeResult(checked=False, passed=True, notes="judge_disabled")

        if not answer.strip():
            return JudgeResult(checked=False, passed=False, notes="empty_answer")

        required = [k for k in required_keywords if isinstance(k, str) and k.strip()]

        judge_prompt = (
            "You are a strict QA judge for recruiter-facing answers. "
            "Check if the answer is faithful to evidence, aligned with intent, and contains required keywords when provided. "
            "If it fails, propose a corrected short answer. "
            "Return ONLY JSON with keys: verdict, reasons, corrected_answer. "
            "verdict must be PASS or FAIL.\n\n"
            f"Language: {language}\n"
            f"Intent: {plan_intent}\n"
            f"Required keywords: {required}\n"
            f"User message: {message}\n"
            f"Current answer: {answer}\n"
            f"Evidence context:\n{sources_context[:3000]}\n"
        )

        try:
            res = self.client.responses.create(
                model=OPENAI_CHAT_MODEL,
                input=[{"role": "user", "content": judge_prompt}],
                temperature=0.0,
            )
            text = getattr(res, "output_text", "") or ""
            obj = self._extract_json(text)
            if not obj:
                return JudgeResult(checked=True, passed=True, notes="unparseable_judge_output")

            verdict = str(obj.get("verdict", "PASS")).upper().strip()
            corrected = str(obj.get("corrected_answer", "")).strip()

            if verdict == "FAIL" and corrected:
                return JudgeResult(checked=True, passed=False, revised_answer=corrected, notes="judge_rewrite")

            return JudgeResult(checked=True, passed=(verdict != "FAIL"), notes="judge_pass")
        except Exception:
            return JudgeResult(checked=False, passed=True, notes="judge_error")

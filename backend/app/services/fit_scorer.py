from .job_matcher import JobMatchResult


class FitScorer:
    @staticmethod
    def score(result: JobMatchResult) -> int:
        required_total = max(len(result.required_skills), 1)

        matched_ratio = len(result.matched_skills) / required_total
        partial_ratio = len(result.partial_matched_skills) / required_total

        # Optimistic but still evidence-based calibration.
        matched_points = int(matched_ratio * 70)
        partial_points = int(partial_ratio * 15)
        project_points = min(len(result.relevant_projects) * 8, 20)

        # Keep some penalty, but less punitive to avoid overly harsh scores.
        missing_penalty = min(len(result.missing_skills) * 2, 12)

        raw = matched_points + partial_points + project_points - missing_penalty

        # Practical floor so serious candidates are not under-scored on sparse JDs.
        floor = 35 if result.required_skills else 45
        return max(min(max(raw, floor), 100), 0)

    @staticmethod
    def label(score: int, language: str) -> str:
        if language == "fr":
            if score >= 85:
                return "Excellent fit"
            if score >= 70:
                return "Tres bon fit"
            if score >= 55:
                return "Bon potentiel"
            return "Fit partiel"

        if score >= 85:
            return "Excellent fit"
        if score >= 70:
            return "Strong fit"
        if score >= 55:
            return "Promising fit"
        return "Partial fit"

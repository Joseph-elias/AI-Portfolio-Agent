from app.services.job_matcher import JobMatchResult


class FitScorer:
    @staticmethod
    def score(result: JobMatchResult) -> int:
        required_total = max(len(result.required_skills), 1)
        required_ratio = len(result.matched_skills) / required_total
        required_points = int(required_ratio * 60)
        project_points = min(len(result.relevant_projects) * 10, 30)
        missing_penalty = min(len(result.missing_skills) * 5, 20)
        return max(min(required_points + project_points - missing_penalty, 100), 0)

    @staticmethod
    def label(score: int, language: str) -> str:
        if language == "fr":
            if score >= 80:
                return "Tres bon fit"
            if score >= 60:
                return "Bon fit"
            if score >= 40:
                return "Fit partiel"
            return "Fit faible"

        if score >= 80:
            return "Strong fit"
        if score >= 60:
            return "Good fit"
        if score >= 40:
            return "Partial fit"
        return "Weak fit"

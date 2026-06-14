import language_tool_python

from models.schemas import GrammarIssue, GrammarResult

MAX_ISSUES_RETURNED = 8
PENALTY_PER_ERROR = 6


class GrammarScoreService:
    def __init__(self) -> None:
        self._tool: language_tool_python.LanguageTool | None = None

    def _get_tool(self) -> language_tool_python.LanguageTool:
        if self._tool is None:
            self._tool = language_tool_python.LanguageTool("en-US")
        return self._tool

    def score(self, text: str) -> GrammarResult:
        tool = self._get_tool()
        matches = tool.check(text)
        word_count = max(len(text.split()), 1)
        error_count = len(matches)

        density_penalty = (error_count / word_count) * 100
        flat_penalty = error_count * PENALTY_PER_ERROR
        raw_score = 100 - max(density_penalty, flat_penalty * 0.5)
        final_score = round(max(0.0, min(100.0, raw_score)), 2)

        issues = [
            GrammarIssue(
                message=match.message,
                context=match.context or text[max(0, match.offset - 20) : match.offset + match.error_length + 20],
                offset=match.offset,
                length=match.error_length,
            )
            for match in matches[:MAX_ISSUES_RETURNED]
        ]

        return GrammarResult(
            score=final_score,
            error_count=error_count,
            issues=issues,
        )


grammar_score_service = GrammarScoreService()

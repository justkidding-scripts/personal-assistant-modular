import re

class SummarizerSkill:
    name = "summarize"

    def can_handle(self, text: str) -> bool:
        return text.lower().startswith("summarize ")

    def handle(self, text: str) -> str:
        # Very simple heuristic summarizer: take first N sentences
        content = text[len("summarize "):].strip()
        sentences = re.split(r"(?<=[.!?])\s+", content)
        if not sentences:
            return "(nothing to summarize)"
        return " ".join(sentences[:3])

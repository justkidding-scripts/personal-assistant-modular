#!/usr/bin/env python3
import os
import re
import requests
from typing import Dict, Any, List

from skills.todos import TodoSkill
from skills.summarizer import SummarizerSkill
from skills.rag import RAGSkill
from skills.health_triage import HealthTriageSkill

class Assistant:
    def __init__(self):
        self.skills = [
            TodoSkill(),
            SummarizerSkill(),
            RAGSkill(),
            HealthTriageSkill(),
        ]

    def handle(self, query: str) -> Dict[str, Any]:
        q = (query or "").strip()
        for s in self.skills:
            if s.can_handle(q):
                result = s.handle(q)
                return {"answer": result, "skill": s.name}
        # fallback to LLM if configured
        llm_answer = self._llm_answer(q)
        return {"answer": llm_answer, "skill": "llm"}

    def _llm_answer(self, prompt: str) -> str:
        # Try Ollama first
        base = os.getenv("OLLAMA_BASE_URL")
        model = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
        if base:
            try:
                r = requests.post(
                    f"{base.rstrip('/')}/api/generate",
                    json={"model": model, "prompt": prompt, "stream": False},
                    timeout=30,
                )
                if r.ok:
                    return (r.json() or {}).get("response", "")
            except Exception:
                pass
        # Then OpenAI-compatible
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com")
            model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            try:
                r = requests.post(
                    f"{base_url.rstrip('/')}/v1/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": "You are a concise personal assistant."},
                            {"role": "user", "content": prompt},
                        ],
                        "temperature": 0.2,
                    },
                    timeout=30,
                )
                if r.ok:
                    data = r.json()
                    return (data.get("choices", [{}])[0]
                                .get("message", {})
                                .get("content", ""))
            except Exception:
                pass
        # Final fallback
        return "(LLM not configured)"

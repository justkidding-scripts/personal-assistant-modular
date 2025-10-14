#!/usr/bin/env python3
import re
from typing import Dict

class HealthTriageSkill:
    name = "triage"

    def can_handle(self, text: str) -> bool:
        t = (text or "").strip().lower()
        return t.startswith("triage ") or t == "triage help"

    def handle(self, text: str) -> str:
        low = (text or "").strip().lower()
        if low == "triage help":
            return (
                "Provide symptoms like: triage chest pain, sweating, shortness of breath.\n"
                "I will format a pre-visit summary for a clinician. This is not medical advice."
            )
        # Extract simple symptom list
        content = text[len("triage "):].strip()
        # Simple parsing: split by commas
        symptoms = [s.strip() for s in content.split(",") if s.strip()]
        flags = []
        critical = {"chest pain", "shortness of breath", "severe bleeding", "unconscious", "stroke"}
        for s in symptoms:
            if s.lower() in critical:
                flags.append(s)
        lines = ["Pre-Visit Summary (Not a Diagnosis)", "", "Reported Symptoms:"]
        for s in symptoms:
            lines.append(f"- {s}")
        lines.append("")
        if flags:
            lines.append("Potential Red Flags Detected:")
            for f in flags:
                lines.append(f"- {f}")
            lines.append("")
            lines.append("If you are experiencing severe or life-threatening symptoms, call local emergency services immediately.")
        lines.append("")
        lines.append("Suggested Next Steps:")
        lines.append("- Share this summary with a qualified clinician.")
        lines.append("- Bring current medications and relevant history to the visit.")
        lines.append("- This is not medical advice.")
        return "\n".join(lines)

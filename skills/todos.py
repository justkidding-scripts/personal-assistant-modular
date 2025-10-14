import re
from typing import List

class TodoSkill:
    name = "todo"

    def __init__(self):
        self.todos: List[str] = []

    def can_handle(self, text: str) -> bool:
        t = text.lower().strip()
        return t.startswith("todo ") or t == "todo list" or t == "todo clear"

    def handle(self, text: str) -> str:
        t = text.strip()
        low = t.lower()
        if low == "todo list":
            if not self.todos:
                return "(empty)"
            return "\n".join(f"- {i+1}. {item}" for i, item in enumerate(self.todos))
        if low == "todo clear":
            self.todos.clear()
            return "Cleared"
        m = re.match(r"todo\s+add\s+(.+)", t, re.I)
        if m:
            item = m.group(1).strip()
            self.todos.append(item)
            return f"Added: {item}"
        return "Try: 'todo add <item>' or 'todo list'"

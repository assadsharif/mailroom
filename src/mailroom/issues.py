"""An issue: its subject, preview and body. Objects go around the code, never raw text."""

import re
from dataclasses import dataclass
from pathlib import Path

ANY_LINK = re.compile(r"\[[^\]]+\]\(([^)\s]+)\)")


@dataclass(frozen=True)
class Issue:
    subject: str | None
    preview: str | None
    body: str

    @classmethod
    def parse(cls, text: str) -> "Issue":
        lines = text.splitlines()
        subject: str | None = None
        preview: str | None = None
        body_lines = lines
        if lines and lines[0].startswith("Subject:"):
            subject = lines[0][len("Subject:"):].strip()
            body_lines = lines[1:]
            if body_lines and body_lines[0].startswith("Preview:"):
                preview = body_lines[0][len("Preview:"):].strip()
                body_lines = body_lines[1:]
        return cls(subject, preview, "\n".join(body_lines).strip())

    @classmethod
    def from_path(cls, path: Path) -> "Issue":
        return cls.parse(path.read_text(encoding="utf-8"))

    @property
    def links(self) -> list[str]:
        return ANY_LINK.findall(self.body)

    def personalize(self, first_name: str) -> str:
        return self.body.replace("{{first_name}}", first_name)

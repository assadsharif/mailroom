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
        subject: str | None = None
        preview: str | None = None
        body_lines: list[str] = []
        for line in text.splitlines():
            if subject is None and line.startswith("Subject:"):
                subject = line[len("Subject:"):].strip()
            elif preview is None and line.startswith("Preview:"):
                preview = line[len("Preview:"):].strip()
            else:
                body_lines.append(line)
        return cls(subject, preview, "\n".join(body_lines).strip())

    @classmethod
    def from_path(cls, path: Path) -> "Issue":
        return cls.parse(path.read_text(encoding="utf-8"))

    @property
    def links(self) -> list[str]:
        return ANY_LINK.findall(self.body)

    def personalize(self, first_name: str) -> str:
        return self.body.replace("{{first_name}}", first_name)

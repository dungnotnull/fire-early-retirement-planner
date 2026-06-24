"""Knowledge-brain sync -- load authoritative evidence and fallback gracefully."""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import List, Optional

from .constants import FRAMEWORKS
from .utils import configure_logging, get_logger

configure_logging()
logger = get_logger("fire_planner.knowledge_sync")


@dataclass
class KnowledgeEntry:
    """One scored entry from the knowledge brain."""

    title: str
    source: str
    relevance: float
    key_finding: str
    date: Optional[str] = None


class KnowledgeBrainSync:
    """Load and query the local SECOND-KNOWLEDGE-BRAIN.md."""

    def __init__(self, brain_path: Optional[str] = None):
        if brain_path is None:
            here = os.path.dirname(os.path.abspath(__file__))
            brain_path = os.path.join(here, "..", "..", "SECOND-KNOWLEDGE-BRAIN.md")
        self.brain_path = os.path.abspath(brain_path)
        self.degraded = False
        self.entries: List[KnowledgeEntry] = []
        self.frameworks = FRAMEWORKS
        self._load()

    def _load(self) -> None:
        if not os.path.exists(self.brain_path):
            logger.warning("Knowledge brain not found at %s; degraded mode.", self.brain_path)
            self.degraded = True
            return
        try:
            with open(self.brain_path, "r", encoding="utf-8") as f:
                text = f.read()
            self.entries = self._parse(text)
            logger.info("Loaded %d knowledge-brain entries", len(self.entries))
        except Exception as exc:
            logger.warning("Could not read knowledge brain (%s); degraded mode.", exc)
            self.degraded = True

    @staticmethod
    def _parse(text: str) -> List[KnowledgeEntry]:
        """Parse date-stamped entries from the markdown brain."""
        entries: List[KnowledgeEntry] = []
        # Match ### [YYYY-MM-DD] Title lines and read until next heading or end
        pattern = re.compile(r"###\s*\[(\d{4}-\d{2}-\d{2})\]\s*(.+?)(?=^###|\Z)", re.M | re.S)
        for match in pattern.finditer(text):
            date, title_block = match.group(1), match.group(2)
            lines = title_block.splitlines()
            title = lines[0].strip()
            source = ""
            relevance = 0.0
            finding = ""
            for line in lines[1:]:
                if line.lower().startswith("- venue/source:"):
                    source = line.split(":", 1)[1].strip()
                elif line.lower().startswith("- relevance score:"):
                    try:
                        relevance = float(line.split(":", 1)[1].strip())
                    except ValueError:
                        relevance = 0.0
                elif line.lower().startswith("- key finding:"):
                    finding = line.split(":", 1)[1].strip()
            entries.append(
                KnowledgeEntry(
                    title=title,
                    source=source,
                    relevance=relevance,
                    key_finding=finding,
                    date=date,
                )
            )
        return entries

    def query(self, keyword: str, top_k: int = 3) -> List[KnowledgeEntry]:
        """Return top-k entries matching a keyword, sorted by relevance."""
        keyword_lower = keyword.lower()
        matches = [
            e
            for e in self.entries
            if keyword_lower in e.title.lower() or keyword_lower in e.key_finding.lower()
        ]
        matches.sort(key=lambda e: e.relevance, reverse=True)
        return matches[:top_k]

    def get_framework_citation(self, framework_key: str) -> str:
        """Return a human-readable citation for a named framework."""
        fw = self.frameworks.get(framework_key, {})
        return f"{fw.get('name', framework_key)} -- {fw.get('authors', '')} ({fw.get('source', '')})"

    def degraded_mode_note(self) -> str:
        if self.degraded:
            return (
                "Live web search unavailable; analysis uses seeded frameworks and assumptions. "
                "Refresh via tools/knowledge_updater.py for latest research."
            )
        return "Knowledge brain loaded; live web sources are unavailable in this run. Using seeded frameworks and static knowledge base."


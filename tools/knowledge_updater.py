#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
knowledge_updater.py -- self-improving knowledge pipeline for `fire-early-retirement-planner`.

Pattern:
  1. crawl4ai / requests -> fetch latest ArXiv papers (q-fin.PM, q-fin.RM, econ.GN)
  2. WebSearch -> latest reports from authoritative domain sources
  3. Parse -> title, authors, date, DOI/URL, abstract, key findings
  4. Score -> recency -- domain-keyword relevance
  5. Append -> scored, date-stamped entries into SECOND-KNOWLEDGE-BRAIN.md
  6. Dedupe -> skip URLs/DOIs already present (hash check)

Recommended schedule: weekly cron.
Graceful degradation: if crawl4ai / network is unavailable, log and exit 0 so the
skill keeps working from the existing knowledge brain.
"""
from __future__ import annotations

import datetime
import hashlib
import logging
import os
import re
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

# Optional dependencies: installed with `pip install -e .[crawl]`
try:
    import requests  # type: ignore
except Exception:  # pragma: no cover
    requests = None  # type: ignore

try:
    import feedparser  # type: ignore
except Exception:  # pragma: no cover
    feedparser = None  # type: ignore

try:
    from crawl4ai import WebCrawler  # type: ignore
except Exception:  # pragma: no cover
    WebCrawler = None  # type: ignore


HERE = os.path.dirname(os.path.abspath(__file__))
BRAIN = os.path.join(HERE, "..", "SECOND-KNOWLEDGE-BRAIN.md")

ARXIV_CATEGORIES = ["q-fin.PM", "q-fin.RM", "econ.GN"]
DOMAIN_SOURCES = [
    "https://www.ssrn.com/",
    "https://www.bogleheads.org/wiki/",
    "https://www.morningstar.com/retirement",
    "https://fred.stlouisfed.org/",
    "https://www.ssa.gov/oact/",
]
SEARCH_QUERIES = [
    "safe withdrawal rate research 2026",
    "sequence of returns risk early retirement",
    "dynamic withdrawal guardrails Guyton Klinger",
    "Monte Carlo retirement success probability study",
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("knowledge_updater")


@dataclass
class Entry:
    """One candidate knowledge-brain entry."""

    title: str
    authors: str
    date: str
    url: str
    abstract: str
    source_type: str = "arxiv"
    relevance: float = 0.0


@dataclass
class PipelineResult:
    """Result of a single update run."""

    appended: int = 0
    skipped_dedupe: int = 0
    skipped_low_relevance: int = 0
    errors: List[str] = field(default_factory=list)


def _hash(url: str) -> str:
    """Stable 16-char hash for deduplication."""
    return hashlib.sha256(url.strip().lower().encode("utf-8")).hexdigest()[:16]


def _existing_hashes(text: str) -> Set[str]:
    return set(re.findall(r"<!--hash:([0-9a-f]{16})-->", text))


def relevance_score(title: str, abstract: str) -> float:
    """Keyword-match relevance score in [0, 1]."""
    blob = (title + " " + abstract).lower()
    hits = 0
    denom = 0
    for kw in SEARCH_QUERIES:
        words = kw.lower().split()
        denom += len(words)
        for w in words:
            if w in blob:
                hits += 1
    if denom == 0:
        return 0.0
    return round(min(1.0, hits / denom), 3)


def fetch_arxiv_feed(category: str, timeout: int = 30) -> List[Entry]:
    """Fetch recent ArXiv RSS entries for a category."""
    if requests is None and feedparser is None:
        logger.warning("Neither requests nor feedparser available; skipping ArXiv.")
        return []
    url = f"http://export.arxiv.org/rss/{category}"
    entries: List[Entry] = []
    try:
        if feedparser is not None:
            parsed = feedparser.parse(url)
            for item in parsed.get("entries", []):
                title = item.get("title", "").strip()
                summary = item.get("summary", "").strip()
                link = item.get("link", "").strip()
                date = item.get("published", datetime.date.today().isoformat())[:10]
                authors = ", ".join(a.get("name", "") for a in item.get("authors", []))
                if link:
                    entries.append(
                        Entry(
                            title=title,
                            authors=authors or "-",
                            date=date,
                            url=link,
                            abstract=summary[:600],
                            source_type="arxiv",
                            relevance=relevance_score(title, summary),
                        )
                    )
        elif requests is not None:
            resp = requests.get(url, timeout=timeout)
            resp.raise_for_status()
            ids = re.findall(r"arXiv:(\d{4}\.\d{4,5})", resp.text)
            for aid in set(ids):
                entries.append(
                    Entry(
                        title=f"arXiv:{aid}",
                        authors="-",
                        date=datetime.date.today().isoformat(),
                        url=f"https://arxiv.org/abs/{aid}",
                        abstract="",
                        source_type="arxiv",
                        relevance=0.0,
                    )
                )
    except Exception as exc:
        logger.warning("ArXiv fetch failed for %s: %s", category, exc)
    return entries


def fetch_domain_source(url: str, timeout: int = 30) -> List[Entry]:
    """Fetch a domain landing page as a dated update entry."""
    if WebCrawler is None and requests is None:
        return []
    try:
        if WebCrawler is not None:
            crawler = WebCrawler()
            crawler.warmup()
            result = crawler.run(url=url)
            text = getattr(result, "markdown", "") or ""
        elif requests is not None:
            text = requests.get(url, timeout=timeout).text[:2000]
        else:
            return []
        return [
            Entry(
                title=f"Update from {url.rstrip('/').split('/')[-1]}",
                authors="-",
                date=datetime.date.today().isoformat(),
                url=url,
                abstract=text[:500],
                source_type="domain",
                relevance=relevance_score(url, text),
            )
        ]
    except Exception as exc:
        logger.warning("Domain fetch failed for %s: %s", url, exc)
        return []


def fetch_websearch(query: str) -> List[Entry]:
    """Placeholder for WebSearch integration.

    Production deployment should wire this to an approved WebSearch tool or API
    (e.g., Bing Web Search API, SerpAPI). When unavailable, the pipeline degrades
    gracefully and relies on ArXiv + domain sources.
    """
    logger.info("WebSearch not configured; skipping query '%s'", query)
    return []


def fetch_entries() -> Tuple[List[Entry], List[str]]:
    """Return candidate entries and a list of non-fatal errors."""
    entries: List[Entry] = []
    errors: List[str] = []

    for category in ARXIV_CATEGORIES:
        entries.extend(fetch_arxiv_feed(category))

    for src in DOMAIN_SOURCES:
        entries.extend(fetch_domain_source(src))

    for query in SEARCH_QUERIES:
        entries.extend(fetch_websearch(query))

    # Remove exact URL duplicates before scoring
    seen_urls: Set[str] = set()
    unique: List[Entry] = []
    for e in entries:
        if e.url and e.url not in seen_urls:
            seen_urls.add(e.url)
            unique.append(e)
    return unique, errors


def append_entries(entries: List[Entry], brain_path: str = BRAIN) -> PipelineResult:
    """Append scored, de-duplicated entries to the knowledge brain."""
    result = PipelineResult()
    if not os.path.exists(brain_path):
        logger.error("Knowledge brain not found at %s", brain_path)
        result.errors.append(f"Brain not found: {brain_path}")
        return result

    with open(brain_path, "r", encoding="utf-8") as f:
        text = f.read()
    seen = _existing_hashes(text)

    today = datetime.date.today().isoformat()
    lines: List[str] = []
    for e in entries:
        url = e.url.strip()
        if not url:
            continue
        h = _hash(url)
        if h in seen:
            result.skipped_dedupe += 1
            continue
        if e.relevance < 0.05:
            result.skipped_low_relevance += 1
            continue
        seen.add(h)
        lines.append(
            f"\n### [{today}] {e.title}\n"
            f"- Authors: {e.authors}\n"
            f"- Venue/Source: {e.url}\n"
            f"- Key finding: {e.abstract[:280]}\n"
            f"- Relevance score: {e.relevance}\n"
            f"<!--hash:{h}-->\n"
        )
        result.appended += 1

    if result.appended:
        with open(brain_path, "a", encoding="utf-8") as f:
            f.write(f"\n<!-- crawl {today}: +{result.appended} entries --\u003e\n")
            f.write("".join(lines))
        logger.info("Appended %d new entries", result.appended)
    else:
        logger.info("No new entries appended")
    return result


def main() -> int:
    logger.info("Starting knowledge_updater for fire-early-retirement-planner")
    entries, errors = fetch_entries()
    if errors:
        for err in errors:
            logger.warning("Fetch error: %s", err)
    result = append_entries(entries)
    logger.info(
        "Done: appended=%d skipped_dedupe=%d skipped_low_relevance=%d",
        result.appended,
        result.skipped_dedupe,
        result.skipped_low_relevance,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Validate the static marketing site before GitHub Pages publishes it."""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_PAGES = [
    "index.html",
    "privacy/index.html",
    "terms/index.html",
    "support/index.html",
    "subscription/index.html",
    "app-store/index.html",
]


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if name in {"href", "src"} and value:
                self.links.append(value)


def resolve_link(source: Path, link: str) -> Path | None:
    parsed = urlparse(link)
    if parsed.scheme in {"http", "https", "mailto"} or link.startswith("#"):
        return None
    clean = parsed.path
    if not clean:
        return None
    target = (source.parent / clean).resolve()
    if target.is_dir() or link.endswith("/"):
        target = target / "index.html"
    return target


def main() -> None:
    errors: list[str] = []
    for page in REQUIRED_PAGES:
        if not (ROOT / page).is_file():
            errors.append(f"Missing required page: {page}")

    for html in ROOT.rglob("*.html"):
        parser = LinkParser()
        parser.feed(html.read_text(encoding="utf-8"))
        for link in parser.links:
            target = resolve_link(html, link)
            if target and not target.exists():
                errors.append(f"{html.relative_to(ROOT)} has broken link: {link}")

    if errors:
        raise SystemExit("\n".join(errors))
    print(f"Validated {len(list(ROOT.rglob('*.html')))} HTML files.")


if __name__ == "__main__":
    main()

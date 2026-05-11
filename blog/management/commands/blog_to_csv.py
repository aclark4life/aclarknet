"""Management command to convert blog repo entries to CSV for import.

Supports three source formats:
- ABlog/Sphinx: YYYY/MM/DD/<slug>/index.rst  (blog-2017, blog-2020)
- Flat RST:     YYYY/MM/DD/<slug>.rst         (aclark4life/blog)
- Pelican HTML: YYYY/MM/DD/<slug>/index.html  (pelican-blog compiled output)

Also supports merging multiple CSVs with deduplication via --merge.
"""

import csv
import os
import re
import sys

from django.core.management.base import BaseCommand, CommandError


POST_DIRECTIVE_RE = re.compile(
    r"\.\. post::\s*(\d{4}[/-]\d{2}[/-]\d{2})", re.IGNORECASE
)
CATEGORY_RE = re.compile(r"^\s+:category:\s*(.+)$", re.IGNORECASE | re.MULTILINE)
UNDERLINE_RE = re.compile(r"^[=\-~^\*#]+$")
DATE_PATH_RE = re.compile(r"(\d{4})[/\\](\d{2})[/\\](\d{1,2})")


def _slug_from_path(path):
    """Extract slug from a relative file path."""
    parts = path.replace("\\", "/").split("/")
    # For YYYY/MM/DD/<slug>/index.{rst,html}: slug is parts[-2]
    # For YYYY/MM/DD/<slug>.rst: slug is parts[-1] without extension
    filename = parts[-1]
    if filename in ("index.rst", "index.html"):
        return parts[-2] if len(parts) >= 2 else ""
    return os.path.splitext(filename)[0]


def _date_from_path(path):
    """Derive pub_date (YYYY-MM-DD) from a path containing YYYY/MM/DD."""
    m = DATE_PATH_RE.search(path.replace("\\", "/"))
    if m:
        year, month, day = m.group(1), m.group(2), m.group(3)
        return f"{year}-{month}-{int(day):02d}"
    return ""


def parse_rst_entry(content, path, source):
    """
    Parse a single RST blog entry and return a dict of fields.

    Handles both ABlog format (with ``.. post::`` directive) and flat RST
    files (title/underline only, date inferred from path).
    """
    lines = content.splitlines()

    # Extract title: first non-empty line whose next non-empty line is an underline
    title = ""
    title_line_idx = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        for j in range(i + 1, len(lines)):
            next_line = lines[j].strip()
            if not next_line:
                continue
            if UNDERLINE_RE.match(next_line) and len(next_line) >= len(stripped):
                title = stripped
                title_line_idx = i
            break
        break

    if not title:
        for line in lines:
            if line.strip():
                title = line.strip()
                break

    slug = _slug_from_path(path)

    # Extract pub_date from .. post:: directive, fall back to path
    pub_date = ""
    post_match = POST_DIRECTIVE_RE.search(content)
    if post_match:
        pub_date = post_match.group(1).replace("/", "-")
    else:
        pub_date = _date_from_path(path)

    # Extract tags/categories
    tags = ""
    cat_match = CATEGORY_RE.search(content)
    if cat_match:
        tags = cat_match.group(1).strip()

    # Extract body
    body = ""
    if post_match:
        block_start = content.index(post_match.group(0))
        after_directive = content[block_start:]
        directive_lines = after_directive.splitlines()
        skip = 1
        for line in directive_lines[1:]:
            if line.startswith(" ") or line.startswith("\t") or not line.strip():
                skip += 1
            else:
                break
        body = "\n".join(directive_lines[skip:]).strip()
    elif title_line_idx is not None:
        start = title_line_idx + 2
        while start < len(lines) and not lines[start].strip():
            start += 1
        body = "\n".join(lines[start:]).strip()
    else:
        body = content.strip()

    return {
        "title": title,
        "slug": slug,
        "pub_date": pub_date,
        "body": body,
        "tags": tags,
        "source": source,
    }


def parse_html_entry(content, path, source):
    """
    Parse a compiled Pelican HTML entry using stdlib html.parser.

    Extracts title from <h1> or <title>, body from <article> or <div class="entry-content">,
    date and slug from path.
    """
    from html.parser import HTMLParser

    class _Parser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.title = ""
            self.body_parts = []
            self._in_title_tag = False
            self._in_h1 = False
            self._in_article = 0
            self._in_entry_content = 0
            self._capture = False

        def handle_starttag(self, tag, attrs):
            attr_dict = dict(attrs)
            classes = attr_dict.get("class", "").split()
            if tag == "title":
                self._in_title_tag = True
            elif tag == "h1":
                self._in_h1 = True
            elif tag == "article":
                self._in_article += 1
                self._capture = True
            elif tag in ("div", "section") and any(
                c in classes
                for c in ("entry-content", "post-content", "article-content")
            ):
                self._in_entry_content += 1
                self._capture = True

        def handle_endtag(self, tag):
            if tag == "title":
                self._in_title_tag = False
            elif tag == "h1":
                self._in_h1 = False
            elif tag == "article":
                self._in_article = max(0, self._in_article - 1)
                if self._in_article == 0:
                    self._capture = False
            elif tag in ("div", "section") and self._in_entry_content > 0:
                self._in_entry_content -= 1
                if self._in_entry_content == 0 and self._in_article == 0:
                    self._capture = False

        def handle_data(self, data):
            if self._in_h1 and not self.title:
                self.title = data.strip()
            elif not self.title and self._in_title_tag:
                self.title = data.strip()
            if self._capture:
                self.body_parts.append(data)

    parser = _Parser()
    parser.feed(content)

    title = parser.title or _slug_from_path(path).replace("-", " ").title()
    body = " ".join(parser.body_parts).strip()

    # Strip site name from title (e.g. "My Post | Alex Clark - ...")
    if " | " in title:
        title = title.split(" | ")[0].strip()
    if " - Python" in title:
        title = title.split(" - Python")[0].strip()

    return {
        "title": title,
        "slug": _slug_from_path(path),
        "pub_date": _date_from_path(path),
        "body": body,
        "tags": "",
        "source": source,
    }


def collect_entries_from_repo(repo_path, source, stderr_write):
    """Walk a repo directory and parse all blog entries found."""
    entries = []
    for dirpath, dirnames, filenames in os.walk(repo_path):
        dirnames[:] = sorted(
            d
            for d in dirnames
            if not d.startswith(".")
            and d not in ("_static", "_themes", "_build", "images", "now", "nginx")
        )

        # ABlog/Sphinx: YYYY/MM/DD/<slug>/index.rst
        if "index.rst" in filenames:
            rst_path = os.path.join(dirpath, "index.rst")
            rel_path = os.path.relpath(rst_path, repo_path)
            # Only treat as blog post if path matches date pattern
            if DATE_PATH_RE.search(rel_path.replace("\\", "/")):
                try:
                    with open(rst_path, encoding="utf-8") as f:
                        content = f.read()
                    entry = parse_rst_entry(content, rel_path, source)
                    if entry["pub_date"]:
                        entries.append(entry)
                except Exception as e:
                    stderr_write(f"Warning: could not parse {rst_path}: {e}")

        # Flat RST: YYYY/MM/DD/<slug>.rst
        for filename in filenames:
            if filename.endswith(".rst") and filename != "index.rst":
                rst_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(rst_path, repo_path)
                if DATE_PATH_RE.search(rel_path.replace("\\", "/")):
                    try:
                        with open(rst_path, encoding="utf-8") as f:
                            content = f.read()
                        entry = parse_rst_entry(content, rel_path, source)
                        if entry["pub_date"]:
                            entries.append(entry)
                    except Exception as e:
                        stderr_write(f"Warning: could not parse {rst_path}: {e}")

        # Pelican compiled HTML: YYYY/MM/DD/<slug>/index.html
        if "index.html" in filenames:
            html_path = os.path.join(dirpath, "index.html")
            rel_path = os.path.relpath(html_path, repo_path)
            if DATE_PATH_RE.search(rel_path.replace("\\", "/")):
                try:
                    with open(html_path, encoding="utf-8") as f:
                        content = f.read()
                    entry = parse_html_entry(content, rel_path, source)
                    if entry["pub_date"] and entry["slug"]:
                        entries.append(entry)
                except Exception as e:
                    stderr_write(f"Warning: could not parse {html_path}: {e}")

    return entries


def merge_and_dedup(all_entries):
    """Merge entries from multiple sources, deduplicating by (pub_date, slug).

    When duplicates exist, prefer RST entries over HTML ones and later sources
    over earlier ones (last-write-wins within same format).
    """
    seen = {}
    for entry in all_entries:
        key = (entry["pub_date"], entry["slug"])
        if key not in seen:
            seen[key] = entry
        else:
            existing = seen[key]
            # Prefer entries with a body; prefer RST over HTML
            existing_is_html = existing.get("source", "").startswith("pelican")
            new_is_html = entry.get("source", "").startswith("pelican")
            if existing_is_html and not new_is_html:
                seen[key] = entry
            elif not existing_is_html and new_is_html:
                pass  # keep existing RST
            elif len(entry.get("body", "")) > len(existing.get("body", "")):
                seen[key] = entry
    return sorted(seen.values(), key=lambda e: e["pub_date"])


def write_csv(entries, output, stdout_write, stderr_write):
    fieldnames = ["title", "slug", "pub_date", "body", "tags", "source"]
    if output == "-":
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(entries)
        stderr_write(f"Wrote {len(entries)} entries to stdout.")
    else:
        with open(output, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(entries)
        stdout_write(f"Wrote {len(entries)} entries to {output}")


class Command(BaseCommand):
    help = (
        "Convert blog entries from cloned repos to CSV for import. "
        "Supports ABlog RST, flat RST, and compiled Pelican HTML formats. "
        "Use --merge to combine multiple CSV files with deduplication."
    )

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            "--repo-path",
            help="Path to a cloned blog repository root.",
        )
        group.add_argument(
            "--merge",
            nargs="+",
            metavar="CSV",
            help="Merge and deduplicate multiple CSV files produced by previous runs.",
        )
        parser.add_argument(
            "--output",
            default="-",
            help="Output CSV file path. Use '-' for stdout (default).",
        )
        parser.add_argument(
            "--source",
            default="",
            help='Source label for entries (e.g. "blog-2017"). Used with --repo-path.',
        )

    def handle(self, *args, **options):
        output = options["output"]

        if options.get("merge"):
            # Merge mode: read multiple CSVs and deduplicate
            all_entries = []
            for csv_path in options["merge"]:
                if not os.path.isfile(csv_path):
                    raise CommandError(f"CSV file not found: {csv_path}")
                with open(csv_path, newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    entries = list(reader)
                all_entries.extend(entries)
                self.stderr.write(f"Read {len(entries)} entries from {csv_path}")
            merged = merge_and_dedup(all_entries)
            self.stderr.write(
                self.style.SUCCESS(
                    f"Merged to {len(merged)} unique entries "
                    f"(from {len(all_entries)} total)."
                )
            )
            write_csv(
                merged,
                output,
                lambda m: self.stdout.write(self.style.SUCCESS(m)),
                lambda m: self.stderr.write(self.style.SUCCESS(m)),
            )
            return

        # Repo mode: parse entries from a repo directory
        repo_path = options["repo_path"]
        source = options["source"]

        if not os.path.isdir(repo_path):
            raise CommandError(f"repo-path does not exist: {repo_path}")

        entries = collect_entries_from_repo(repo_path, source, self.stderr.write)
        entries.sort(key=lambda e: e["pub_date"])

        self.stderr.write(f"Found {len(entries)} entries in {repo_path}")
        write_csv(
            entries,
            output,
            lambda m: self.stdout.write(self.style.SUCCESS(m)),
            lambda m: self.stderr.write(self.style.SUCCESS(m)),
        )

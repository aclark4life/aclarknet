"""Management command to convert RST blog repo entries to CSV for import."""

import csv
import os
import re
import sys

from django.core.management.base import BaseCommand, CommandError


POST_DIRECTIVE_RE = re.compile(
    r"\.\. post::\s*(\d{4}[/-]\d{2}[/-]\d{2})", re.IGNORECASE
)
CATEGORY_RE = re.compile(r"^\s+:category:\s*(.+)$", re.IGNORECASE | re.MULTILINE)
UNDERLINE_RE = re.compile(r"^[=\-~^]+$")


def parse_rst_entry(content, path, source):
    """
    Parse a single RST blog entry and return a dict of fields.

    Expected RST format::

        Title Here
        ==========

        .. post:: YYYY/MM/DD
            :category: Tag1, Tag2

        Body content...
    """
    lines = content.splitlines()

    # Extract title: first non-empty line whose next non-empty line is an underline
    title = ""
    title_line_idx = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        # Look ahead for underline
        for j in range(i + 1, len(lines)):
            next_line = lines[j].strip()
            if not next_line:
                continue
            if UNDERLINE_RE.match(next_line):
                title = stripped
                title_line_idx = i
            break
        break

    if not title:
        # Fall back: use first non-empty line
        for line in lines:
            if line.strip():
                title = line.strip()
                break

    # Extract slug from path: YYYY/MM/DD/<slug>/index.rst
    parts = path.replace("\\", "/").split("/")
    slug = ""
    if len(parts) >= 2:
        # The slug is the directory containing index.rst
        slug = parts[-2]

    # Extract pub_date from .. post:: directive, fall back to path
    pub_date = ""
    post_match = POST_DIRECTIVE_RE.search(content)
    if post_match:
        raw_date = post_match.group(1).replace("/", "-")
        pub_date = raw_date
    else:
        # Derive from path: look for YYYY/MM/DD pattern in parts
        for i, part in enumerate(parts):
            if re.match(r"^\d{4}$", part) and i + 2 < len(parts):
                year = part
                month = parts[i + 1]
                day = parts[i + 2]
                if re.match(r"^\d{2}$", month) and re.match(r"^\d{1,2}$", day):
                    pub_date = f"{year}-{month}-{int(day):02d}"
                    break

    # Extract tags/categories from :category: inside .. post:: block
    tags = ""
    cat_match = CATEGORY_RE.search(content)
    if cat_match:
        tags = cat_match.group(1).strip()

    # Extract body: everything after the .. post:: block
    body = ""
    post_match2 = POST_DIRECTIVE_RE.search(content)
    if post_match2:
        # Find end of the .. post:: directive block (ends when indentation stops)
        block_start = content.index(post_match2.group(0))
        after_directive = content[block_start:]
        # Skip the directive line and any indented option lines
        directive_lines = after_directive.splitlines()
        skip = 1  # skip ".. post:: ..."
        for line in directive_lines[1:]:
            if line.startswith(" ") or line.startswith("\t") or not line.strip():
                skip += 1
            else:
                break
        body = "\n".join(directive_lines[skip:]).strip()
    elif title_line_idx is not None:
        # Fall back: body starts after title + underline
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


class Command(BaseCommand):
    help = "Convert RST blog entries from a cloned repo to a CSV file for import."

    def add_arguments(self, parser):
        parser.add_argument(
            "--repo-path",
            required=True,
            help="Path to the cloned blog repository root.",
        )
        parser.add_argument(
            "--output",
            default="-",
            help="Output CSV file path. Use '-' for stdout (default).",
        )
        parser.add_argument(
            "--source",
            default="",
            help='Source label to tag entries with (e.g. "blog-2017").',
        )

    def handle(self, *args, **options):
        repo_path = options["repo_path"]
        output = options["output"]
        source = options["source"]

        if not os.path.isdir(repo_path):
            raise CommandError(f"repo-path does not exist: {repo_path}")

        entries = []
        for dirpath, dirnames, filenames in os.walk(repo_path):
            # Skip hidden directories
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]
            if "index.rst" in filenames:
                rst_path = os.path.join(dirpath, "index.rst")
                try:
                    with open(rst_path, encoding="utf-8") as f:
                        content = f.read()
                    rel_path = os.path.relpath(rst_path, repo_path)
                    entry = parse_rst_entry(content, rel_path, source)
                    if entry["pub_date"]:  # only include entries with a date
                        entries.append(entry)
                except Exception as e:
                    self.stderr.write(f"Warning: could not parse {rst_path}: {e}")

        entries.sort(key=lambda e: e["pub_date"])

        fieldnames = ["title", "slug", "pub_date", "body", "tags", "source"]

        if output == "-":
            writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(entries)
            self.stderr.write(
                self.style.SUCCESS(f"Wrote {len(entries)} entries to stdout.")
            )
        else:
            with open(output, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(entries)
            self.stdout.write(
                self.style.SUCCESS(f"Wrote {len(entries)} entries to {output}")
            )

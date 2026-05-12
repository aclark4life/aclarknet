"""Export blog entries from the database (or CSV) to data/posts/*.rst files.

Each file is named YYYY-MM-DD-slug.rst and contains RST front-matter followed
by the original body content.

Usage:
    python manage.py export_rst_posts
    python manage.py export_rst_posts --from-csv data/blog_entries.csv
    python manage.py export_rst_posts --output-dir data/posts
"""

import csv
import pathlib
import re

from django.core.management.base import BaseCommand

SAFE_RE = re.compile(r"[^\w-]")


def slug_to_safe(slug):
    return SAFE_RE.sub("-", slug).strip("-")


def entry_to_rst(title, slug, pub_date, tags, source, status, body):
    """Return RST file content with front-matter field list."""
    lines = [
        f":title: {title}",
        f":date: {pub_date}",
        f":slug: {slug}",
    ]
    if tags:
        lines.append(f":tags: {tags}")
    if source:
        lines.append(f":source: {source}")
    lines.append(f":status: {status}")
    lines.append("")  # blank line separating front-matter from body
    if body:
        lines.append(body.rstrip())
    lines.append("")  # trailing newline
    return "\n".join(lines)


class Command(BaseCommand):
    help = "Export blog entries to data/posts/*.rst files."

    def add_arguments(self, parser):
        parser.add_argument(
            "--from-csv",
            default=None,
            help="Export from a CSV file instead of the database.",
        )
        parser.add_argument(
            "--output-dir",
            default="data/posts",
            help="Directory to write RST files into (default: data/posts).",
        )
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Overwrite existing .rst files.",
        )

    def handle(self, *args, **options):
        output_dir = pathlib.Path(options["output_dir"])
        output_dir.mkdir(parents=True, exist_ok=True)

        if options["from_csv"]:
            entries = self._load_csv(options["from_csv"])
        else:
            entries = self._load_db()

        written = skipped = 0
        for entry in entries:
            filename = f"{entry['pub_date']}-{slug_to_safe(entry['slug'])}.rst"
            path = output_dir / filename
            if path.exists() and not options["overwrite"]:
                skipped += 1
                continue
            content = entry_to_rst(
                title=entry["title"],
                slug=entry["slug"],
                pub_date=entry["pub_date"],
                tags=entry.get("tags", ""),
                source=entry.get("source", ""),
                status=entry.get("status", "published"),
                body=entry.get("body", ""),
            )
            path.write_text(content, encoding="utf-8")
            written += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Exported {written} entries to {output_dir}/ "
                f"({skipped} skipped — already exist, use --overwrite to replace)."
            )
        )

    def _load_csv(self, csv_path):
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return [{k.lower().strip(): v for k, v in row.items()} for row in reader]

    def _load_db(self):
        from blog.models import Entry

        return [
            {
                "title": e.title,
                "slug": e.slug,
                "pub_date": str(e.pub_date),
                "tags": e.tags,
                "source": e.source,
                "status": e.status,
                "body": e.body,
            }
            for e in Entry.objects.all()
        ]

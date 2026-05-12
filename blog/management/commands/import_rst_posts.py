"""Import blog entries from data/posts/*.rst files into the database.

Each .rst file must be named YYYY-MM-DD-slug.rst and begin with a RST
field-list front-matter block:

    :title: My Post Title
    :date: 2003-06-15
    :slug: my-post-slug
    :tags: python, plone
    :source: blog
    :status: published

    Body content in RST format follows after the blank line...

The date and slug in the filename are authoritative. Front-matter fields
override filename-derived values when present. Upserts on (pub_date, slug).

Usage:
    python manage.py import_rst_posts
    python manage.py import_rst_posts --posts-dir data/posts
    python manage.py import_rst_posts --dry-run
"""

import datetime
import pathlib
import re

from django.core.management.base import BaseCommand, CommandError

# Matches :fieldname: value lines at the start of the file
_FIELD_RE = re.compile(r"^:(\w+):\s*(.*)", re.MULTILINE)
# Matches YYYY-MM-DD-slug in filename
_FILENAME_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-(.+)\.rst$")


def parse_rst_file(path):
    """Return (metadata dict, body str) from an RST file with front-matter."""
    text = path.read_text(encoding="utf-8")

    meta = {}
    # Collect consecutive field-list lines from the top
    body_start = 0
    for line in text.splitlines(keepends=True):
        m = _FIELD_RE.match(line)
        if m:
            meta[m.group(1).lower()] = m.group(2).strip()
            body_start += len(line)
        elif line.strip() == "" and meta:
            # First blank line after front-matter ends it
            body_start += len(line)
            break
        else:
            # Non-field line before any fields — no front-matter
            break

    body = text[body_start:].strip()
    return meta, body


def parse_filename(filename):
    """Return (date_str, slug) from YYYY-MM-DD-slug.rst, or (None, None)."""
    m = _FILENAME_RE.match(filename)
    if m:
        return m.group(1), m.group(2)
    return None, None


class Command(BaseCommand):
    help = "Import blog entries from data/posts/*.rst files."

    def add_arguments(self, parser):
        parser.add_argument(
            "--posts-dir",
            default="data/posts",
            help="Directory containing .rst files (default: data/posts).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Parse and report without writing to the database.",
        )
        parser.add_argument(
            "--status",
            default=None,
            help="Override status for all imported entries (published/draft).",
        )
        parser.add_argument(
            "--sync",
            action="store_true",
            help="Delete DB entries that have no matching .rst file (by pub_date+slug).",
        )

    def handle(self, *args, **options):
        from blog.models import Entry

        posts_dir = pathlib.Path(options["posts_dir"])
        if not posts_dir.exists():
            raise CommandError(f"Posts directory not found: {posts_dir}")

        rst_files = sorted(posts_dir.glob("*.rst"))
        if not rst_files:
            self.stdout.write(self.style.WARNING(f"No .rst files found in {posts_dir}"))
            return

        created = updated = skipped = errors = 0

        for path in rst_files:
            date_str, slug_from_file = parse_filename(path.name)
            if not date_str:
                self.stderr.write(
                    f"Skipping {path.name} — filename must be YYYY-MM-DD-slug.rst"
                )
                errors += 1
                continue

            try:
                meta, body = parse_rst_file(path)
            except Exception as e:
                self.stderr.write(f"Error reading {path.name}: {e}")
                errors += 1
                continue

            # Front-matter overrides filename; filename is fallback
            slug = meta.get("slug", slug_from_file)
            date_str = meta.get("date", date_str)
            title = meta.get("title", "")
            tags = meta.get("tags", "")
            source = meta.get("source", "")
            status = options["status"] or meta.get("status", Entry.PUBLISHED)

            if not title:
                self.stderr.write(
                    f"Skipping {path.name} — missing :title: in front-matter"
                )
                errors += 1
                continue

            try:
                pub_date = datetime.date.fromisoformat(date_str)
            except ValueError:
                self.stderr.write(f"Skipping {path.name} — invalid date: {date_str!r}")
                errors += 1
                continue

            if options["dry_run"]:
                self.stdout.write(f"  [dry-run] {pub_date} {slug!r} — {title!r}")
                continue

            obj, created_flag = Entry.objects.update_or_create(
                pub_date=pub_date,
                slug=slug,
                defaults={
                    "title": title,
                    "body": body,
                    "tags": tags,
                    "source": source,
                    "status": status,
                },
            )
            if created_flag:
                created += 1
            else:
                updated += 1

        if options["dry_run"]:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Dry run complete — {len(rst_files)} files parsed, {errors} errors."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Import complete: {created} created, {updated} updated, "
                    f"{skipped} skipped, {errors} errors."
                )
            )

        if options.get("sync") and not options["dry_run"]:
            # Build set of (pub_date, slug) keys present in RST files
            rst_keys = set()
            for path in rst_files:
                date_str, slug_from_file = parse_filename(path.name)
                if not date_str:
                    continue
                try:
                    meta, _ = parse_rst_file(path)
                except Exception:
                    continue
                slug = meta.get("slug", slug_from_file)
                date_str = meta.get("date", date_str)
                try:
                    pub_date = datetime.date.fromisoformat(date_str)
                except ValueError:
                    continue
                rst_keys.add((pub_date, slug))

            deleted = 0
            for entry in Entry.objects.all():
                if (entry.pub_date, entry.slug) not in rst_keys:
                    self.stdout.write(
                        f"  Deleting orphan: {entry.pub_date} {entry.slug!r}"
                    )
                    entry.delete()
                    deleted += 1
            self.stdout.write(
                self.style.SUCCESS(f"Sync complete: {deleted} orphan(s) deleted.")
            )

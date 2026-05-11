"""Management command to import blog entries from a CSV file into the database."""

import csv
import os

from django.core.management.base import BaseCommand, CommandError

from blog.models import Entry


class Command(BaseCommand):
    help = (
        "Import blog entries from a CSV file into the database. "
        "Skips entries that already exist (matched by pub_date + slug). "
        "CSV must have columns: title, slug, pub_date, body, tags, source."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--csv",
            required=True,
            dest="csv_path",
            help="Path to the CSV file to import.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Parse and validate the CSV but do not write to the database.",
        )
        parser.add_argument(
            "--update",
            action="store_true",
            help="Update existing entries (by pub_date+slug) with new data from CSV.",
        )

    def handle(self, *args, **options):
        csv_path = options["csv_path"]
        dry_run = options["dry_run"]
        update = options["update"]

        if not os.path.isfile(csv_path):
            raise CommandError(f"CSV file not found: {csv_path}")

        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        if not rows:
            self.stdout.write("CSV is empty — nothing to import.")
            return

        required = {"title", "slug", "pub_date"}
        if not required.issubset(set(reader.fieldnames or [])):
            missing = required - set(reader.fieldnames or [])
            raise CommandError(f"CSV is missing required columns: {missing}")

        created_count = 0
        updated_count = 0
        skipped_count = 0
        error_count = 0

        for i, row in enumerate(rows, start=2):  # row 1 is the header
            title = (row.get("title") or "").strip()
            slug = (row.get("slug") or "").strip()
            pub_date_str = (row.get("pub_date") or "").strip()
            body = (row.get("body") or "").strip()
            tags = (row.get("tags") or "").strip()
            source = (row.get("source") or "").strip()

            if not title or not slug or not pub_date_str:
                self.stderr.write(
                    f"Row {i}: skipping — missing title, slug, or pub_date "
                    f"(title={title!r}, slug={slug!r}, pub_date={pub_date_str!r})"
                )
                error_count += 1
                continue

            try:
                from datetime import date

                parts = pub_date_str.split("-")
                pub_date = date(int(parts[0]), int(parts[1]), int(parts[2]))
            except (ValueError, IndexError):
                self.stderr.write(
                    f"Row {i}: skipping — invalid pub_date {pub_date_str!r}"
                )
                error_count += 1
                continue

            if dry_run:
                created_count += 1
                continue

            try:
                entry, created = Entry.objects.get_or_create(
                    pub_date=pub_date,
                    slug=slug,
                    defaults={
                        "title": title,
                        "body": body,
                        "tags": tags,
                        "source": source,
                    },
                )
                if created:
                    created_count += 1
                elif update:
                    entry.title = title
                    entry.body = body
                    entry.tags = tags
                    entry.source = source
                    entry.save()
                    updated_count += 1
                else:
                    skipped_count += 1
            except Exception as e:
                self.stderr.write(f"Row {i}: error saving entry {slug!r}: {e}")
                error_count += 1

        verb = "Would import" if dry_run else "Imported"
        self.stdout.write(
            self.style.SUCCESS(
                f"{verb} {created_count} new entries"
                + (f", updated {updated_count}" if updated_count else "")
                + (f", skipped {skipped_count} existing" if skipped_count else "")
                + (f", {error_count} errors" if error_count else "")
                + "."
            )
        )

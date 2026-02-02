"""
Django management command to import notes from CSV file.

This command imports notes from notes_import.csv into the Note model.
"""

import csv
from datetime import datetime
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from db.models import Note
from siteuser.models import SiteUser


class Command(BaseCommand):
    """
    Django management command to import notes from CSV file.

    Imports notes from notes_import.csv with fields:
    - id: Original note ID (not used, Django creates new IDs)
    - created: Creation timestamp
    - updated: Last update timestamp
    - name: Note name/title
    - description: Note content/description
    - user_id: User ID to associate with note

    Usage Examples:
        # Import from default file (notes_import.csv in project root)
        python manage.py import_notes

        # Import from custom file path
        python manage.py import_notes --file /path/to/notes.csv

        # Dry run (don't actually create notes)
        python manage.py import_notes --dry-run

        # Skip notes with missing user_id
        python manage.py import_notes --skip-missing-users
    """

    help = "Import notes from CSV file (notes_import.csv)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default="notes_import.csv",
            help="Path to CSV file to import (default: notes_import.csv)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Perform a dry run without creating notes",
        )
        parser.add_argument(
            "--skip-missing-users",
            action="store_true",
            help="Skip notes with missing user_id instead of failing",
        )

    def handle(self, *args, **options):
        file_path = options["file"]
        dry_run = options["dry_run"]
        skip_missing_users = options["skip_missing_users"]

        # Check if file exists
        csv_file = Path(file_path)
        if not csv_file.exists():
            raise CommandError(f"CSV file not found: {file_path}")

        self.stdout.write(f"Reading notes from: {file_path}")

        if dry_run:
            self.stdout.write(
                self.style.WARNING("DRY RUN MODE - No notes will be created")
            )

        created_count = 0
        skipped_count = 0
        error_count = 0

        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row_num, row in enumerate(
                reader, start=2
            ):  # Start at 2 (header is row 1)
                try:
                    # Parse timestamps
                    created = self._parse_timestamp(row.get("created"))
                    updated = self._parse_timestamp(row.get("updated"))

                    # Get user if user_id is provided
                    user = None
                    user_id = row.get("user_id", "").strip()
                    if user_id:
                        try:
                            user = SiteUser.objects.get(pk=user_id)
                        except SiteUser.DoesNotExist:
                            if skip_missing_users:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f"Row {row_num}: Skipping - User {user_id} not found"
                                    )
                                )
                                skipped_count += 1
                                continue
                            else:
                                raise CommandError(
                                    f"Row {row_num}: User with ID {user_id} not found. "
                                    "Use --skip-missing-users to skip these notes."
                                )

                    # Prepare note data
                    # Clean up literal \r\n escape sequences in the text
                    description = row.get("description", "").strip()
                    description = description.replace("\\r\\n", "\n").replace(
                        "\\r", "\n"
                    )

                    name = row.get("name", "").strip()
                    name = name.replace("\\r\\n", " ").replace("\\r", " ")

                    note_data = {
                        "name": name,
                        "description": description,
                        "user": user,
                    }

                    if not dry_run:
                        # Create the note
                        note = Note.objects.create(**note_data)

                        # Update timestamps if provided
                        if created:
                            Note.objects.filter(pk=note.pk).update(created=created)
                        if updated:
                            Note.objects.filter(pk=note.pk).update(updated=updated)

                        created_count += 1
                        self.stdout.write(f"Row {row_num}: Created note '{note.name}'")
                    else:
                        created_count += 1
                        self.stdout.write(
                            f"Row {row_num}: Would create note '{note_data['name']}'"
                        )

                except Exception as e:
                    error_count += 1
                    self.stdout.write(
                        self.style.ERROR(f"Row {row_num}: Error - {str(e)}")
                    )

        # Summary
        self.stdout.write("\n" + "=" * 50)
        if dry_run:
            self.stdout.write(self.style.SUCCESS("DRY RUN COMPLETE"))
            self.stdout.write(f"Would create: {created_count} notes")
        else:
            self.stdout.write(self.style.SUCCESS("IMPORT COMPLETE"))
            self.stdout.write(self.style.SUCCESS(f"Created: {created_count} notes"))

        if skipped_count > 0:
            self.stdout.write(self.style.WARNING(f"Skipped: {skipped_count} notes"))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f"Errors: {error_count} notes"))

    def _parse_timestamp(self, timestamp_str):
        """Parse timestamp string to datetime object."""
        if not timestamp_str or not timestamp_str.strip():
            return None

        try:
            # Try parsing with timezone info (e.g., "2024-09-30 19:24:37.74451+00")
            dt = datetime.fromisoformat(timestamp_str.replace("+00", "+00:00"))
            return timezone.make_aware(dt) if timezone.is_naive(dt) else dt
        except ValueError:
            try:
                # Try parsing without timezone
                dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f")
                return timezone.make_aware(dt)
            except ValueError:
                self.stdout.write(
                    self.style.WARNING(f"Could not parse timestamp: {timestamp_str}")
                )
                return None

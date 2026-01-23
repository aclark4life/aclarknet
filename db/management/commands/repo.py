"""
Django management command for repository operations.

This command provides git repository management functionality including
syncing with upstream repositories.
"""

import subprocess

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """
    Django management command to manage repository operations.

    Provides functionality to sync local repository with upstream by
    fetching and rebasing.

    Usage Examples:
        # Sync with upstream (fetch and rebase)
        python manage.py repo sync

        # Sync with custom upstream remote
        python manage.py repo sync --upstream origin

        # Sync specific branch
        python manage.py repo sync --branch develop
    """

    help = "Manage repository operations (sync with upstream)"

    def add_arguments(self, parser):
        parser.add_argument(
            "action",
            type=str,
            choices=["sync"],
            help="Repository action to perform",
        )
        parser.add_argument(
            "--upstream",
            default="upstream",
            help="Upstream remote name (default: upstream)",
        )
        parser.add_argument(
            "--branch",
            default=None,
            help="Branch to sync (default: current branch)",
        )

    def handle(self, *args, **options):
        action = options["action"]
        upstream = options["upstream"]
        branch = options["branch"]

        try:
            if action == "sync":
                self._sync_repo(upstream, branch)
        except subprocess.CalledProcessError as e:
            raise CommandError(f"Git command failed: {e}")
        except Exception as e:
            raise CommandError(f"Error: {e}")

    def _sync_repo(self, upstream, branch):
        """Fetch from upstream and rebase the current/specified branch."""
        # Get current branch if not specified
        if branch is None:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                check=True,
                timeout=10,
            )
            branch = result.stdout.strip()
            self.stdout.write(f"Current branch: {branch}")

        # Check if upstream remote exists
        result = subprocess.run(
            ["git", "remote"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
        remotes = result.stdout.strip().split("\n")

        if upstream not in remotes:
            raise CommandError(
                f"Remote '{upstream}' not found. Available remotes: {', '.join(remotes)}"
            )

        # Fetch from upstream
        self.stdout.write(f"Fetching from {upstream}...")
        subprocess.run(["git", "fetch", upstream], check=True, timeout=300)
        self.stdout.write(self.style.SUCCESS(f"✓ Fetched from {upstream}"))

        # Rebase on upstream branch
        self.stdout.write(f"Rebasing {branch} on {upstream}/{branch}...")
        result = subprocess.run(
            ["git", "rebase", f"{upstream}/{branch}"],
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode != 0:
            error_msg = (
                f"✗ Rebase failed:\n{result.stderr}\n\n"
                "To abort the rebase, run: git rebase --abort"
            )
            raise CommandError(error_msg)

        self.stdout.write(
            self.style.SUCCESS(f"✓ Rebased {branch} on {upstream}/{branch}")
        )
        self.stdout.write(
            self.style.SUCCESS("\n✓ Repository synced successfully!")
        )

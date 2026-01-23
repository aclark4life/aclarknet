"""Tests for repo management command."""

import subprocess
from io import StringIO
from unittest.mock import patch, MagicMock

from django.core.management import call_command, CommandError
from django.test import TestCase


class RepoCommandTest(TestCase):
    """Test the repo management command."""

    @patch("subprocess.run")
    def test_sync_gets_current_branch(self, mock_run):
        """Test that sync command gets current branch when not specified."""
        # Mock git rev-parse to return a branch name
        mock_result = MagicMock()
        mock_result.stdout = "main\n"
        mock_result.returncode = 0
        
        # Mock git remote to return available remotes
        mock_remote_result = MagicMock()
        mock_remote_result.stdout = "origin\nupstream\n"
        mock_remote_result.returncode = 0
        
        # Mock git fetch
        mock_fetch_result = MagicMock()
        mock_fetch_result.returncode = 0
        
        # Mock git rebase
        mock_rebase_result = MagicMock()
        mock_rebase_result.returncode = 0
        mock_rebase_result.stderr = ""
        
        mock_run.side_effect = [
            mock_result,  # git rev-parse
            mock_remote_result,  # git remote
            mock_fetch_result,  # git fetch
            mock_rebase_result,  # git rebase
        ]
        
        out = StringIO()
        call_command("repo", "sync", stdout=out)
        
        output = out.getvalue()
        self.assertIn("main", output)
        self.assertIn("synced successfully", output.lower())

    @patch("subprocess.run")
    def test_sync_with_custom_branch(self, mock_run):
        """Test that sync command uses specified branch."""
        # Mock git remote to return available remotes
        mock_remote_result = MagicMock()
        mock_remote_result.stdout = "origin\nupstream\n"
        mock_remote_result.returncode = 0
        
        # Mock git fetch
        mock_fetch_result = MagicMock()
        mock_fetch_result.returncode = 0
        
        # Mock git rebase
        mock_rebase_result = MagicMock()
        mock_rebase_result.returncode = 0
        mock_rebase_result.stderr = ""
        
        mock_run.side_effect = [
            mock_remote_result,  # git remote
            mock_fetch_result,  # git fetch
            mock_rebase_result,  # git rebase
        ]
        
        out = StringIO()
        call_command("repo", "sync", "--branch=develop", stdout=out)
        
        output = out.getvalue()
        self.assertIn("develop", output)
        self.assertIn("synced successfully", output.lower())

    @patch("subprocess.run")
    def test_sync_with_custom_upstream(self, mock_run):
        """Test that sync command uses specified upstream remote."""
        # Mock git rev-parse to return a branch name
        mock_result = MagicMock()
        mock_result.stdout = "main\n"
        mock_result.returncode = 0
        
        # Mock git remote to return available remotes
        mock_remote_result = MagicMock()
        mock_remote_result.stdout = "origin\nfork\n"
        mock_remote_result.returncode = 0
        
        # Mock git fetch
        mock_fetch_result = MagicMock()
        mock_fetch_result.returncode = 0
        
        # Mock git rebase
        mock_rebase_result = MagicMock()
        mock_rebase_result.returncode = 0
        mock_rebase_result.stderr = ""
        
        mock_run.side_effect = [
            mock_result,  # git rev-parse
            mock_remote_result,  # git remote
            mock_fetch_result,  # git fetch
            mock_rebase_result,  # git rebase
        ]
        
        out = StringIO()
        call_command("repo", "sync", "--upstream=fork", stdout=out)
        
        output = out.getvalue()
        self.assertIn("fork", output)

    @patch("subprocess.run")
    def test_sync_fails_with_missing_upstream(self, mock_run):
        """Test that sync command fails when upstream remote doesn't exist."""
        # Mock git rev-parse to return a branch name
        mock_result = MagicMock()
        mock_result.stdout = "main\n"
        mock_result.returncode = 0
        
        # Mock git remote to return only origin
        mock_remote_result = MagicMock()
        mock_remote_result.stdout = "origin\n"
        mock_remote_result.returncode = 0
        
        mock_run.side_effect = [
            mock_result,  # git rev-parse
            mock_remote_result,  # git remote
        ]
        
        with self.assertRaises(CommandError) as cm:
            call_command("repo", "sync", stdout=StringIO())
        
        self.assertIn("upstream", str(cm.exception).lower())
        self.assertIn("not found", str(cm.exception).lower())

    @patch("subprocess.run")
    def test_sync_handles_rebase_failure(self, mock_run):
        """Test that sync command handles rebase failures gracefully."""
        # Mock git rev-parse to return a branch name
        mock_result = MagicMock()
        mock_result.stdout = "main\n"
        mock_result.returncode = 0
        
        # Mock git remote to return available remotes
        mock_remote_result = MagicMock()
        mock_remote_result.stdout = "origin\nupstream\n"
        mock_remote_result.returncode = 0
        
        # Mock git fetch
        mock_fetch_result = MagicMock()
        mock_fetch_result.returncode = 0
        
        # Mock git rebase failure
        mock_rebase_result = MagicMock()
        mock_rebase_result.returncode = 1
        mock_rebase_result.stderr = "Rebase conflict detected"
        
        mock_run.side_effect = [
            mock_result,  # git rev-parse
            mock_remote_result,  # git remote
            mock_fetch_result,  # git fetch
            mock_rebase_result,  # git rebase
        ]
        
        # The command should exit with code 1 on rebase failure
        with self.assertRaises(SystemExit):
            call_command("repo", "sync", stdout=StringIO(), stderr=StringIO())

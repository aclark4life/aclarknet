"""Custom allauth adapters for social authentication."""

import os
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.core.exceptions import ImmediateHttpResponse
from django.shortcuts import render


class GitHubWhitelistAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter to restrict GitHub login to whitelisted usernames.

    The whitelist is configured via the GITHUB_USERNAME_WHITELIST environment variable,
    which should be a comma-separated list of GitHub usernames.

    Example: GITHUB_USERNAME_WHITELIST=user1,user2,user3
    """

    def pre_social_login(self, request, sociallogin):
        """
        Invoked just after a user successfully authenticates via a social provider,
        but before the login is actually processed.

        This is where we check if the GitHub username is in the whitelist.
        """
        # Only check for GitHub provider
        if sociallogin.account.provider != "github":
            return

        # Get the whitelist from environment variable
        whitelist_str = os.environ.get("GITHUB_USERNAME_WHITELIST", "")

        # If no whitelist is configured, allow all users (backward compatible)
        if not whitelist_str:
            return

        # Parse the whitelist (comma-separated usernames, strip whitespace)
        whitelist = [
            username.strip()
            for username in whitelist_str.split(",")
            if username.strip()
        ]

        # If whitelist is empty after parsing, allow all users
        if not whitelist:
            return

        # Get the GitHub username from the social account data
        github_username = sociallogin.account.extra_data.get("login", "")

        # Check if the username is in the whitelist
        if github_username not in whitelist:
            # Reject the login
            error_message = f"Access denied. GitHub username '{github_username}' is not authorized to login."

            # Render a custom error page
            response = render(
                request,
                "socialaccount/authentication_error.html",
                {
                    "error_message": error_message,
                    "github_username": github_username,
                },
            )
            raise ImmediateHttpResponse(response)


class NoSignupAccountAdapter(DefaultAccountAdapter):
    """
    Custom adapter to disable regular account signups.
    Users can only login with existing accounts, not create new ones.
    """

    def is_open_for_signup(self, request):
        """
        Disable signups by always returning False.
        """
        return False


class NoSignupSocialAccountAdapter(GitHubWhitelistAdapter):
    """
    Custom adapter that combines GitHub whitelist functionality with controlled signups.

    - Inherits GitHub username whitelist from GitHubWhitelistAdapter
    - Allows whitelisted GitHub users to auto-create accounts on first login
    - Blocks non-whitelisted users from creating accounts
    - For non-GitHub providers, signups are disabled
    """

    def is_open_for_signup(self, request, sociallogin):
        """
        Allow signups only for whitelisted GitHub users.
        Block signups for all other cases.
        """
        # For GitHub, check if user is whitelisted
        if sociallogin.account.provider == "github":
            whitelist_str = os.environ.get("GITHUB_USERNAME_WHITELIST", "")

            # If no whitelist configured, block signups (secure by default)
            if not whitelist_str:
                return False

            # Parse whitelist
            whitelist = [
                username.strip()
                for username in whitelist_str.split(",")
                if username.strip()
            ]

            # If whitelist is empty after parsing, block signups
            if not whitelist:
                return False

            # Get GitHub username
            github_username = sociallogin.account.extra_data.get("login", "")

            # Allow signup only if user is in whitelist
            return github_username in whitelist

        # For all other providers, disable signups
        return False

    def pre_social_login(self, request, sociallogin):
        """
        Check GitHub whitelist (from parent class).
        If user passes whitelist, they can login or auto-create account.
        """
        # Apply GitHub whitelist check from parent class
        # This will raise ImmediateHttpResponse if user is not whitelisted
        super().pre_social_login(request, sociallogin)

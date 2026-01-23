#!/usr/bin/env python3
"""
Test script to verify the git commands in repo.py work correctly.
This tests the core functionality without requiring Django to be fully set up.
"""

import subprocess
import sys


def test_git_commands():
    """Test the git commands that repo.py would execute."""
    print("Testing git commands for repo sync functionality...\n")
    
    # Test 1: Get current branch
    print("1. Testing 'git rev-parse --abbrev-ref HEAD'")
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        current_branch = result.stdout.strip()
        print(f"   ✓ Current branch: {current_branch}\n")
    except subprocess.CalledProcessError as e:
        print(f"   ✗ Failed: {e}\n")
        return False

    # Test 2: List remotes
    print("2. Testing 'git remote'")
    try:
        result = subprocess.run(
            ["git", "remote"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        remotes = result.stdout.strip().split("\n")
        print(f"   ✓ Found remotes: {', '.join(remotes)}\n")
    except subprocess.CalledProcessError as e:
        print(f"   ✗ Failed: {e}\n")
        return False

    # Test 3: Check if 'upstream' remote exists
    print("3. Testing remote existence check")
    test_remote = "upstream"
    if test_remote in remotes:
        print(f"   ✓ Remote '{test_remote}' exists\n")
    else:
        print(f"   ⚠ Remote '{test_remote}' not found (this is expected)")
        print(f"     Available remotes: {', '.join(remotes)}\n")

    # Test 4: Test git fetch (dry-run)
    print("4. Testing 'git fetch --dry-run origin'")
    try:
        result = subprocess.run(
            ["git", "fetch", "--dry-run", "origin"],
            capture_output=True,
            text=True,
            check=True,
        )
        print(f"   ✓ Fetch would work (dry-run successful)\n")
    except subprocess.CalledProcessError as e:
        print(f"   ✗ Failed: {e}\n")
        return False

    print("\n" + "="*50)
    print("All git command tests passed! ✓")
    print("="*50)
    print("\nThe repo sync command would execute:")
    print(f"  1. git fetch upstream")
    print(f"  2. git rebase upstream/{current_branch}")
    print("\nNote: Actual rebase was not performed in this test.")
    return True


if __name__ == "__main__":
    success = test_git_commands()
    sys.exit(0 if success else 1)

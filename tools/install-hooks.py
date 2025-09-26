#!/usr/bin/env python3
"""
Git Hooks Installation Script for Spacecraft Subsystem Limits

This script installs Git hooks to automatically build the dist/ folder
when changes are committed to the limits/ folder.
"""

import os
import shutil
import stat
from pathlib import Path


def make_executable(file_path):
    """Make a file executable on Unix-like systems."""
    try:
        current_mode = file_path.stat().st_mode
        executable_mode = current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        file_path.chmod(executable_mode)
        return True
    except Exception as e:
        print(f"WARNING: Could not make {file_path} executable: {e}")
        return False


def install_git_hooks():
    """Install Git hooks for automatic building."""
    print("Installing Git Hooks for Spacecraft Subsystem Limits")
    print("=" * 55)
    
    # Get project root directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # Check if this is a Git repository
    git_dir = project_root / ".git"
    if not git_dir.exists():
        print("ERROR: This is not a Git repository!")
        print("   Please run 'git init' first.")
        return False
    
    # Create hooks directory if it doesn't exist
    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(exist_ok=True)
    
    # Source hooks directory
    source_hooks_dir = project_root / ".githooks"
    if not source_hooks_dir.exists():
        print("ERROR: .githooks directory not found!")
        return False
    
    # Install pre-commit hook
    source_hook = source_hooks_dir / "pre-commit"
    target_hook = hooks_dir / "pre-commit"
    
    if source_hook.exists():
        try:
            shutil.copy2(source_hook, target_hook)
            make_executable(target_hook)
            print(f"Installed: {target_hook}")
        except Exception as e:
            print(f"ERROR: Could not install pre-commit hook: {e}")
            return False
    else:
        print("ERROR: Source pre-commit hook not found!")
        return False
    
    # Create a post-commit hook to re-lock files after commit
    post_commit_content = '''#!/bin/bash
# Post-commit hook to re-lock dist files after successful commit

if [ -f "dist/master.csv" ] || [ -f "dist/latest.json" ] || [ -f "dist/manifest.json" ]; then
    echo "Re-locking dist files..."
    python tools/build.py > /dev/null 2>&1 || true
fi
'''
    
    post_commit_hook = hooks_dir / "post-commit"
    try:
        with open(post_commit_hook, 'w', encoding='utf-8', newline='\n') as f:
            f.write(post_commit_content)
        make_executable(post_commit_hook)
        print(f"Created: {post_commit_hook}")
    except Exception as e:
        print(f"ERROR: Could not create post-commit hook: {e}")
        return False
    
    print()
    print("Git hooks installed successfully!")
    print()
    print("What happens now:")
    print("   - When you commit changes to limits/ folder:")
    print("     1. Pre-commit hook runs build.py automatically")
    print("     2. Updated dist/ files are added to the commit")
    print("     3. Post-commit hook re-locks the dist/ files")
    print()
    print("To test: Make changes to any CSV in limits/ and commit")
    
    return True


def main():
    """Main function."""
    try:
        success = install_git_hooks()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\nInstallation cancelled by user")
        return 1
    except Exception as e:
        print(f"ERROR: {e}")
        return 1


if __name__ == "__main__":
    exit(main())

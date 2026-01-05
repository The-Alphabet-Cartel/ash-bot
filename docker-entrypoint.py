#!/usr/bin/env python3
# ============================================================================
# Ash-Bot v5.0 Container Entrypoint Script
# ============================================================================
# FILE VERSION: v5.0-entrypoint-1.1
# LAST MODIFIED: 2026-01-05
# Repository: https://github.com/the-alphabet-cartel/ash-bot
# Community: The Alphabet Cartel - https://discord.gg/alphabetcartel
# ============================================================================
#
# This script handles runtime user/group ID configuration similar to
# LinuxServer.io containers. It allows specifying PUID and PGID environment
# variables to control what user the container runs as.
#
# ENVIRONMENT VARIABLES:
#   PUID - User ID to run as (default: 1001)
#   PGID - Group ID to run as (default: 1001)
#
# ============================================================================
"""
Container entrypoint for Ash-Bot with PUID/PGID support.

Handles runtime user/group ID configuration for NAS environments.
"""

import os
import pwd
import grp
import sys
import subprocess
from pathlib import Path


# =============================================================================
# Configuration
# =============================================================================

DEFAULT_UID = 1001
DEFAULT_GID = 1001
APP_USER = "bot"
APP_HOME = Path("/app")


# =============================================================================
# Logging Functions
# =============================================================================

def log_info(message: str) -> None:
    """Log an info message."""
    print(f"[entrypoint] INFO: {message}", flush=True)


def log_warn(message: str) -> None:
    """Log a warning message."""
    print(f"[entrypoint] WARN: {message}", flush=True)


def log_error(message: str) -> None:
    """Log an error message."""
    print(f"[entrypoint] ERROR: {message}", file=sys.stderr, flush=True)


# =============================================================================
# User/Group Setup
# =============================================================================

def get_current_uid_gid(username: str) -> tuple[int | None, int | None]:
    """Get current UID and GID for a user."""
    try:
        user_info = pwd.getpwnam(username)
        return user_info.pw_uid, user_info.pw_gid
    except KeyError:
        return None, None


def get_group_gid(groupname: str) -> int | None:
    """Get GID for a group."""
    try:
        group_info = grp.getgrnam(groupname)
        return group_info.gr_gid
    except KeyError:
        return None


def modify_group(groupname: str, new_gid: int) -> bool:
    """Modify a group's GID."""
    try:
        subprocess.run(
            ["groupmod", "-o", "-g", str(new_gid), groupname],
            check=True,
            capture_output=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        log_error(f"Failed to modify group: {e}")
        return False


def modify_user(username: str, new_uid: int, new_gid: int) -> bool:
    """Modify a user's UID and ensure they're in the correct group."""
    try:
        # Modify UID
        subprocess.run(
            ["usermod", "-o", "-u", str(new_uid), username],
            check=True,
            capture_output=True,
        )
        # Ensure user is in correct primary group
        subprocess.run(
            ["usermod", "-g", str(new_gid), username],
            check=True,
            capture_output=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        log_error(f"Failed to modify user: {e}")
        return False


def setup_user(puid: int, pgid: int) -> bool:
    """Configure user and group with specified IDs."""
    log_info("━" * 64)
    log_info("  🤖 Ash-Bot Container Starting")
    log_info("━" * 64)
    log_info(f"  PUID: {puid}")
    log_info(f"  PGID: {pgid}")
    log_info("━" * 64)

    # Check if running as root
    if os.getuid() != 0:
        log_warn("Not running as root - skipping user/group modification")
        log_info(f"Running as UID: {os.getuid()}, GID: {os.getgid()}")
        return True

    # Get current user/group info
    current_uid, current_gid = get_current_uid_gid(APP_USER)
    current_group_gid = get_group_gid(APP_USER)

    # Modify group if needed
    if current_group_gid is not None and current_group_gid != pgid:
        log_info(f"Modifying group {APP_USER} GID from {current_group_gid} to {pgid}")
        if not modify_group(APP_USER, pgid):
            return False

    # Modify user if needed
    if current_uid is not None and current_uid != puid:
        log_info(f"Modifying user {APP_USER} UID from {current_uid} to {puid}")
        if not modify_user(APP_USER, puid, pgid):
            return False
    elif current_uid is not None:
        # UID is correct, but ensure GID is set
        try:
            subprocess.run(
                ["usermod", "-g", str(pgid), APP_USER],
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError:
            pass  # Non-critical

    log_info(f"User {APP_USER} configured with UID:{puid} GID:{pgid}")
    return True


# =============================================================================
# Permission Setup
# =============================================================================

def fix_permissions(puid: int, pgid: int) -> None:
    """Fix ownership of application directories."""
    if os.getuid() != 0:
        return

    log_info("Fixing permissions on application directories...")

    directories_to_fix = [
        APP_HOME / "logs",
        APP_HOME / "src" / "config",
    ]

    for directory in directories_to_fix:
        if directory.exists():
            try:
                for path in directory.rglob("*"):
                    os.chown(path, puid, pgid)
                os.chown(directory, puid, pgid)
            except OSError as e:
                log_warn(f"Could not fix permissions on {directory}: {e}")

    log_info("Permissions configured")


# =============================================================================
# Process Execution
# =============================================================================

def drop_privileges_and_exec(puid: int, pgid: int, command: list[str]) -> None:
    """Drop privileges to specified user and execute command."""
    if os.getuid() == 0:
        # Get user info for home directory
        try:
            user_info = pwd.getpwnam(APP_USER)
            home_dir = user_info.pw_dir
        except KeyError:
            home_dir = str(APP_HOME)

        # Set environment for the new user
        os.environ["HOME"] = home_dir
        os.environ["USER"] = APP_USER
        os.environ["LOGNAME"] = APP_USER

        # Drop privileges - order matters! GID first, then UID
        os.setgid(pgid)
        os.setuid(puid)

        log_info(f"Dropped privileges to UID:{os.getuid()} GID:{os.getgid()}")

    log_info("━" * 64)
    log_info("  Starting application...")
    log_info("━" * 64)

    # Execute the command
    os.execvp(command[0], command)


# =============================================================================
# Main
# =============================================================================

def main() -> None:
    """Main entrypoint function."""
    # Get PUID/PGID from environment
    puid = int(os.environ.get("PUID", DEFAULT_UID))
    pgid = int(os.environ.get("PGID", DEFAULT_GID))

    # Setup user and permissions
    if not setup_user(puid, pgid):
        log_error("Failed to setup user - exiting")
        sys.exit(1)

    fix_permissions(puid, pgid)

    # Get command to run (everything after the entrypoint)
    if len(sys.argv) > 1:
        command = sys.argv[1:]
    else:
        # Default command
        command = ["python", "main.py"]

    # Drop privileges and execute
    drop_privileges_and_exec(puid, pgid, command)


if __name__ == "__main__":
    main()

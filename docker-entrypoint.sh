#!/bin/bash
# ============================================================================
# Ash-Bot v5.0 Container Entrypoint Script
# ============================================================================
# FILE VERSION: v5.0-entrypoint-1.0
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

set -e

# =============================================================================
# Configuration
# =============================================================================

# Default user/group IDs
PUID=${PUID:-1001}
PGID=${PGID:-1001}

# Application user name (internal to container)
APP_USER="bot"
APP_HOME="/app"

# =============================================================================
# Functions
# =============================================================================

log_info() {
    echo "[entrypoint] INFO: $1"
}

log_warn() {
    echo "[entrypoint] WARN: $1"
}

log_error() {
    echo "[entrypoint] ERROR: $1" >&2
}

# =============================================================================
# User/Group Setup
# =============================================================================

setup_user() {
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_info "  🤖 Ash-Bot Container Starting"
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_info "  PUID: ${PUID}"
    log_info "  PGID: ${PGID}"
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # Check if we're running as root (required for user modification)
    if [ "$(id -u)" -ne 0 ]; then
        log_warn "Not running as root - skipping user/group modification"
        log_info "Running as UID: $(id -u), GID: $(id -g)"
        return 0
    fi

    # Get current UID/GID of the app user
    CURRENT_UID=$(id -u ${APP_USER} 2>/dev/null || echo "")
    CURRENT_GID=$(id -g ${APP_USER} 2>/dev/null || echo "")

    # Check if group needs to be modified
    if [ -n "$(getent group ${APP_USER})" ]; then
        CURRENT_GROUP_GID=$(getent group ${APP_USER} | cut -d: -f3)
        if [ "${CURRENT_GROUP_GID}" != "${PGID}" ]; then
            log_info "Modifying group ${APP_USER} GID from ${CURRENT_GROUP_GID} to ${PGID}"
            groupmod -o -g "${PGID}" ${APP_USER}
        fi
    else
        log_info "Creating group ${APP_USER} with GID ${PGID}"
        groupadd -o -g "${PGID}" ${APP_USER}
    fi

    # Check if user needs to be modified
    if [ -n "${CURRENT_UID}" ]; then
        if [ "${CURRENT_UID}" != "${PUID}" ]; then
            log_info "Modifying user ${APP_USER} UID from ${CURRENT_UID} to ${PUID}"
            usermod -o -u "${PUID}" ${APP_USER}
        fi
    else
        log_info "Creating user ${APP_USER} with UID ${PUID}"
        useradd -o -u "${PUID}" -g "${PGID}" -s /bin/bash -d "${APP_HOME}" ${APP_USER}
    fi

    # Ensure user is in the correct group
    usermod -g "${PGID}" ${APP_USER} 2>/dev/null || true

    log_info "User ${APP_USER} configured with UID:${PUID} GID:${PGID}"
}

# =============================================================================
# Permission Setup
# =============================================================================

fix_permissions() {
    # Only fix permissions if running as root
    if [ "$(id -u)" -ne 0 ]; then
        return 0
    fi

    log_info "Fixing permissions on application directories..."

    # Fix ownership of application directories
    chown -R ${PUID}:${PGID} ${APP_HOME}/logs 2>/dev/null || true
    
    # Ensure config directory is readable
    if [ -d "${APP_HOME}/src/config" ]; then
        chown -R ${PUID}:${PGID} ${APP_HOME}/src/config 2>/dev/null || true
    fi

    log_info "Permissions configured"
}

# =============================================================================
# Main Execution
# =============================================================================

main() {
    # Setup user/group
    setup_user

    # Fix permissions
    fix_permissions

    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_info "  Starting application..."
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # If running as root, switch to the app user
    if [ "$(id -u)" -eq 0 ]; then
        exec gosu ${APP_USER} "$@"
    else
        # Not root, just run the command directly
        exec "$@"
    fi
}

# Run main with all passed arguments
main "$@"

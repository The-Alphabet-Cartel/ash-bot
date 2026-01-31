"""
============================================================================
Ash-Bot: Crisis Detection Discord Bot
The Alphabet Cartel - https://discord.gg/alphabetcartel | alphabetcartel.org
============================================================================

MISSION - NEVER TO BE VIOLATED:
    Monitor  → Send messages to Ash-NLP for crisis classification
    Alert    → Notify Crisis Response Team via embeds when crisis detected
    Track    → Maintain user history for escalation pattern detection
    Protect  → Safeguard our LGBTQIA+ community through early intervention

============================================================================
Secrets Manager for Ash-Bot Service
----------------------------------------------------------------------------
FILE VERSION: v5.0-4-1.0-1
LAST MODIFIED: 2026-01-17
PHASE: Phase 4 - Alerting Integration
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
============================================================================

RESPONSIBILITIES:
- Read secrets from Docker Secrets (/run/secrets/)
- Fallback to local secrets directory for development
- Provide secure access to sensitive credentials
- Never log or expose secret values

DOCKER SECRETS LOCATIONS:
- Production (Docker): /run/secrets/<secret_name>
- Development (Local): ./secrets/<secret_name>

SUPPORTED SECRETS:
- claude_api_token: Claude API key for Claude AI access
- huggingface_token: HuggingFace API token for model downloads
- ash_bot_discord_alert_token: Discord webhook URL for Ash-Bot alerts
- ash_bot_token: Discord bot token
- webhook_token: Webhook signing secret
- redis_token: Redis password for secure connections
"""

import logging
import os
from pathlib import Path
from typing import Dict, Optional

# Module version
__version__ = "v5.0-3-5.5-2"

# Initialize logger
logger = logging.getLogger(__name__)

# =============================================================================
# Constants
# =============================================================================

# Docker Secrets mount path (standard Docker location)
DOCKER_SECRETS_PATH = Path("/run/secrets")

# Local development secrets path (relative to project root)
LOCAL_SECRETS_PATH = Path("secrets")

# Known secret names and their descriptions
KNOWN_SECRETS = {
    "ash_bot_discord_alert_token": "Discord webhook URL for Ash-Bot alerts",
    "claude_api_token": "Claude API key for Claude AI access",
    "ash_bot_token": "Discord bot token",
    "huggingface_token": "HuggingFace API token for authenticated model downloads",
    "postgres_token": "PostgreSQL password for secure connections",
    "redis_token": "Redis password for secure connections",
    "webhook_token": "Webhook signing secret",
}

# =============================================================================
# Secrets Manager Class
# =============================================================================


class SecretsManager:
    """
    Manages access to Docker Secrets and local development secrets.

    Reads secrets from:
    1. Docker Secrets path (/run/secrets/) - Production
    2. Local secrets directory (./secrets/) - Development fallback
    3. Environment variables - Last resort fallback

    Attributes:
        docker_path: Path to Docker secrets directory
        local_path: Path to local secrets directory
        _cache: Cached secret values (read once)

    Example:
        >>> secrets = SecretsManager()
        >>> hf_token = secrets.get("huggingface")
        >>> if hf_token:
        ...     print("HuggingFace token loaded")
    """

    def __init__(
        self,
        docker_path: Optional[Path] = None,
        local_path: Optional[Path] = None,
    ):
        """
        Initialize the SecretsManager.

        Args:
            docker_path: Custom Docker secrets path (default: /run/secrets)
            local_path: Custom local secrets path (default: ./secrets)
        """
        self.docker_path = docker_path or DOCKER_SECRETS_PATH
        self.local_path = local_path or self._find_local_secrets_path()
        self._cache: Dict[str, Optional[str]] = {}

        # Log initialization (without revealing paths that might hint at secrets)
        logger.debug("SecretsManager initialized")

    def _find_local_secrets_path(self) -> Path:
        """
        Find the local secrets directory.

        Searches in order:
        1. ./secrets (current directory)
        2. ../secrets (parent directory)
        3. Project root /secrets

        Returns:
            Path to secrets directory
        """
        # Try current directory
        if LOCAL_SECRETS_PATH.exists():
            return LOCAL_SECRETS_PATH

        # Try relative to this file's location
        module_path = Path(__file__).parent.parent.parent / "secrets"
        if module_path.exists():
            return module_path

        # Default to standard path
        return LOCAL_SECRETS_PATH

    def get(
        self,
        secret_name: str,
        default: Optional[str] = None,
        required: bool = False,
    ) -> Optional[str]:
        """
        Get a secret value.

        Lookup order:
        1. Cache (if previously loaded)
        2. Docker Secrets (/run/secrets/<name>)
        3. Local secrets file (./secrets/<name>)
        4. Environment variable (uppercase, prefixed)
        5. Default value

        Args:
            secret_name: Name of the secret (e.g., "huggingface")
            default: Default value if secret not found
            required: If True, raise error when secret not found

        Returns:
            Secret value or default

        Raises:
            SecretNotFoundError: If required=True and secret not found
        """
        # Check cache first
        if secret_name in self._cache:
            return self._cache[secret_name]

        value = None
        source = None

        # 1. Try Docker Secrets path
        docker_secret_path = self.docker_path / secret_name
        if docker_secret_path.exists() and docker_secret_path.is_file():
            try:
                value = docker_secret_path.read_text().strip()
                source = "docker_secrets"
            except Exception as e:
                logger.warning(f"Failed to read Docker secret '{secret_name}': {e}")

        # 2. Try local secrets path
        if value is None:
            local_secret_path = self.local_path / secret_name
            if local_secret_path.exists() and local_secret_path.is_file():
                try:
                    value = local_secret_path.read_text().strip()
                    source = "local_file"
                except Exception as e:
                    logger.warning(f"Failed to read local secret '{secret_name}': {e}")

        # 3. Try environment variable
        if value is None:
            env_var_name = self._get_env_var_name(secret_name)
            value = os.environ.get(env_var_name)
            if value:
                source = "environment"

        # 4. Use default
        if value is None:
            value = default
            source = "default" if default else None

        # Handle required secrets
        if value is None and required:
            raise SecretNotFoundError(
                f"Required secret '{secret_name}' not found. "
                f"Checked: Docker Secrets, local file, environment variable."
            )

        # Cache the value
        self._cache[secret_name] = value

        # Log (without revealing the value)
        if value is not None and source:
            logger.debug(f"Secret '{secret_name}' loaded from {source}")
        elif value is None:
            logger.debug(f"Secret '{secret_name}' not found")

        return value

    def _get_env_var_name(self, secret_name: str) -> str:
        """
        Convert secret name to environment variable name.

        Examples:
            huggingface -> NLP_SECRET_HUGGINGFACE
            discord_token -> NLP_SECRET_DISCORD_TOKEN

        Args:
            secret_name: Secret name

        Returns:
            Environment variable name
        """
        return f"NLP_SECRET_{secret_name.upper()}"

    def get_claude_api_token(self) -> Optional[str]:
        """
        Get Claude API token.

        Also checks CLAUDE_API_TOKEN environment variable as fallback
        (standard Claude environment variable).

        Returns:
            Claude API token or None
        """
        # Try our secrets system first
        token = self.get("claude_api_token")

        # Fallback to standard Claude env vars
        if token is None:
            token = os.environ.get("CLAUDE_API_TOKEN")

        return token

    def get_discord_alert_token(self) -> Optional[str]:
        """
        Get Discord alert webhook token for Ash-Bot.

        Uses the module-specific secret name `ash_bot_discord_alert_token`.
        Also checks ASH_BOT_DISCORD_ALERT_TOKEN environment variable as fallback.

        Returns:
            Discord alert webhook URL or None
        """
        # Try our secrets system first (new module-specific name)
        token = self.get("ash_bot_discord_alert_token")

        # Fallback to environment variable
        if token is None:
            token = os.environ.get("ASH_BOT_DISCORD_ALERT_TOKEN")

        # Legacy fallback (deprecated - will be removed)
        if token is None:
            token = self.get("discord_alert_token")
        if token is None:
            token = os.environ.get("DISCORD_ALERT_TOKEN")

        return token

    def get_ash_bot_token(self) -> Optional[str]:
        """
        Get Discord bot token.

        Also checks ASH_BOT_TOKEN environment variable as fallback
        (standard Discord environment variable).

        Returns:
            Discord bot token or None
        """
        # Try our secrets system first
        token = self.get("ash_bot_token")

        # Fallback to standard Discord env vars
        if token is None:
            token = os.environ.get("ASH_BOT_TOKEN")

        return token

    def get_huggingface_token(self) -> Optional[str]:
        """
        Get HuggingFace API token.

        Also checks HF_TOKEN environment variable as fallback
        (standard HuggingFace environment variable).

        Returns:
            HuggingFace token or None
        """
        # Try our secrets system first
        token = self.get("huggingface")

        # Fallback to standard HuggingFace env vars
        if token is None:
            token = os.environ.get("HF_TOKEN")
        if token is None:
            token = os.environ.get("HUGGING_FACE_HUB_TOKEN")

        return token

    def get_postgres_token(self) -> Optional[str]:
        """
        Get Postgres Token.

        Also checks POSTGRES_TOKEN environment variable as fallback
        (standard Postgres environment variable).

        Returns:
            Postgres Token or None
        """
        # Try our secrets system first
        token = self.get("postgres_token")

        # Fallback to standard Postgres env vars
        if token is None:
            token = os.environ.get("POSTGRES_TOKEN")

        return token

    def get_redis_token(self) -> Optional[str]:
        """
        Get Redis Token.

        Also checks REDIS_TOKEN environment variable as fallback
        (standard Redis environment variable).

        Returns:
            Redis Token or None
        """
        # Try our secrets system first
        token = self.get("redis_token")

        # Fallback to standard Redis env vars
        if token is None:
            token = os.environ.get("REDIS_TOKEN")

        return token

    def get_webhook_token(self) -> Optional[str]:
        """
        Get Webhook Token.

        Also checks WEBHOOK_TOKEN environment variable as fallback
        (standard Webhook environment variable).

        Returns:
            Webhook Token or None
        """
        # Try our secrets system first
        token = self.get("webhook_token")

        # Fallback to standard Webhook env vars
        if token is None:
            token = os.environ.get("WEBHOOK_TOKEN")

        return token

    def has_secret(self, secret_name: str) -> bool:
        """
        Check if a secret exists (without loading it).

        Args:
            secret_name: Name of the secret

        Returns:
            True if secret exists
        """
        # Check Docker path
        if (self.docker_path / secret_name).exists():
            return True

        # Check local path
        if (self.local_path / secret_name).exists():
            return True

        # Check environment
        if os.environ.get(self._get_env_var_name(secret_name)):
            return True

        # Check HuggingFace-specific env vars
        if secret_name == "huggingface":
            if os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN"):
                return True

        return False

    def list_available(self) -> Dict[str, bool]:
        """
        List all known secrets and their availability.

        Returns:
            Dict mapping secret name to availability
        """
        return {name: self.has_secret(name) for name in KNOWN_SECRETS}

    def get_status(self) -> Dict[str, any]:
        """
        Get secrets manager status.

        Returns:
            Status dictionary (safe for logging)
        """
        return {
            "docker_secrets_path": str(self.docker_path),
            "docker_secrets_available": self.docker_path.exists(),
            "local_secrets_path": str(self.local_path),
            "local_secrets_available": self.local_path.exists(),
            "secrets_available": self.list_available(),
            "cached_count": len(self._cache),
        }

    def clear_cache(self) -> None:
        """Clear the secrets cache."""
        self._cache.clear()
        logger.debug("Secrets cache cleared")

    def configure_huggingface(self) -> bool:
        """
        Configure HuggingFace library with token if available.

        Sets the HF_TOKEN environment variable for the transformers
        library to use during model downloads.

        Returns:
            True if token was configured, False otherwise
        """
        token = self.get_huggingface_token()

        if token:
            # Set environment variable for HuggingFace library
            os.environ["HF_TOKEN"] = token
            logger.info("HuggingFace token configured")
            return True
        else:
            logger.debug("No HuggingFace token available (public models only)")
            return False


# =============================================================================
# Exceptions
# =============================================================================


class SecretNotFoundError(Exception):
    """Raised when a required secret is not found."""

    pass


# =============================================================================
# Factory Function
# =============================================================================


def create_secrets_manager(
    docker_path: Optional[Path] = None,
    local_path: Optional[Path] = None,
) -> SecretsManager:
    """
    Factory function to create a SecretsManager instance.

    Following Clean Architecture v5.1 Rule #1: Factory Functions.

    Args:
        docker_path: Custom Docker secrets path
        local_path: Custom local secrets path

    Returns:
        Configured SecretsManager instance

    Example:
        >>> secrets = create_secrets_manager()
        >>> token = secrets.get_huggingface_token()
    """
    return SecretsManager(
        docker_path=docker_path,
        local_path=local_path,
    )


# =============================================================================
# Module-level convenience functions
# =============================================================================

# Global instance (lazy initialization)
_global_secrets_manager: Optional[SecretsManager] = None


def get_secrets_manager() -> SecretsManager:
    """
    Get the global SecretsManager instance.

    Creates instance on first call (lazy initialization).

    Returns:
        Global SecretsManager instance
    """
    global _global_secrets_manager

    if _global_secrets_manager is None:
        _global_secrets_manager = create_secrets_manager()

    return _global_secrets_manager


def get_secret(secret_name: str, default: Optional[str] = None) -> Optional[str]:
    """
    Convenience function to get a secret value.

    Args:
        secret_name: Name of the secret
        default: Default value if not found

    Returns:
        Secret value or default
    """
    return get_secrets_manager().get(secret_name, default)


# =============================================================================
# Export public interface
# =============================================================================

__all__ = [
    "SecretsManager",
    "create_secrets_manager",
    "get_secrets_manager",
    "get_secret",
    "SecretNotFoundError",
    "KNOWN_SECRETS",
]

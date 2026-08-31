"""Domain errors that are safe to present without exposing configuration data."""


class ProfileValidationError(ValueError):
    """An imported profile is malformed or contains a credential."""


class TransactionError(RuntimeError):
    """A configuration write failed and was rolled back where possible."""

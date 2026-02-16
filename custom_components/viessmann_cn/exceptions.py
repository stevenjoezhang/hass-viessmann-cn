"""Exceptions for Viessmann API."""


class ViessmannError(Exception):
    """Base exception for Viessmann API."""


class AuthError(ViessmannError):
    """Authentication failed."""


class NetworkError(ViessmannError):
    """Network communication error."""


class ApiError(ViessmannError):
    """API returned an error."""

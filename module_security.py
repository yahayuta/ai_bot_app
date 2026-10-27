"""Request authentication helpers for the webhook and scheduled-job endpoints.

Every check fails closed: if the secret it needs is not configured, the
request is rejected rather than accepted.
"""
import base64
import functools
import hashlib
import hmac
import os

from flask import request  # type: ignore


def _same(a: str, b: str) -> bool:
    """Constant-time comparison that also accepts non-ASCII input."""
    return hmac.compare_digest(a.encode("utf-8"), b.encode("utf-8"))


def _env(name: str) -> str:
    # Read at request time so a redeploy with new env vars (or tests) takes effect.
    return os.environ.get(name, "")


def verify_line_signature(body: bytes, signature: str | None, channel_secret: str) -> bool:
    """Check the X-Line-Signature header (base64 HMAC-SHA256 of the raw body)."""
    if not channel_secret or not signature:
        return False
    digest = hmac.new(channel_secret.encode("utf-8"), body, hashlib.sha256).digest()
    expected = base64.b64encode(digest).decode("ascii")
    return _same(expected, signature)


def verify_facebook_signature(body: bytes, signature_header: str | None, app_secret: str) -> bool:
    """Check the X-Hub-Signature-256 header ("sha256=<hex HMAC of the raw body>")."""
    if not app_secret or not signature_header or not signature_header.startswith("sha256="):
        return False
    expected = hmac.new(app_secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return _same(expected, signature_header[len("sha256="):])


def verify_job_token(token: str | None) -> bool:
    """Check the shared token sent by Cloud Scheduler (or another trusted caller)."""
    expected = _env("JOB_TOKEN")
    if not expected or not token:
        return False
    return _same(expected, token)


def verify_facebook_verify_token(mode: str | None, token: str | None, expected: str) -> bool:
    """Check the hub.verify_token Meta sends when the webhook URL is registered."""
    if not expected or mode != "subscribe" or not token:
        return False
    return _same(expected, token)


def require_job_token(view):
    """Protect an endpoint so only callers that send `X-Job-Token: <JOB_TOKEN>` can run it."""

    @functools.wraps(view)
    def wrapper(*args, **kwargs):
        if not verify_job_token(request.headers.get("X-Job-Token")):
            if not _env("JOB_TOKEN"):
                print("JOB_TOKEN is not set; rejecting scheduled-job request")
            return "Forbidden", 403
        return view(*args, **kwargs)

    return wrapper

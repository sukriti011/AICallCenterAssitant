"""
Guardrails for the call-center pipeline.

Provides:
  - PII redaction  (SSN, credit-card, phone, email, account numbers)
  - Prompt-injection detection in transcript text
  - Compliance-flag allowlist validation
  - Audio-size validation before Whisper API calls
"""

import re

from app.core.logging import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# PII patterns
# ---------------------------------------------------------------------------
_PII_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    # SSN: 123-45-6789
    ("ssn", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    # Credit card: 16 digits with optional spaces/dashes
    ("credit_card", re.compile(r"\b(?:\d{4}[\s\-]?){3}\d{4}\b")),
    # US phone numbers in common formats
    ("phone", re.compile(r"\b\+?1?[\s.\-]?\(?\d{3}\)?[\s.\-]?\d{3}[\s.\-]?\d{4}\b")),
    # Email addresses
    ("email", re.compile(r"\b[a-zA-Z0-9_.+\-]+@[a-zA-Z0-9\-]+\.[a-zA-Z]{2,}\b", re.IGNORECASE)),
    # Account / acct followed by 6-12 digits
    ("account_number", re.compile(r"\b(?:account|acct)[\s#:]*\d{6,12}\b", re.IGNORECASE)),
]

# ---------------------------------------------------------------------------
# Prompt-injection detector
# ---------------------------------------------------------------------------
_INJECTION_RE = re.compile(
    r"ignore\s+(?:all\s+)?(?:previous\s+)?instructions?"
    r"|forget\s+(?:your\s+)?(?:previous\s+)?instructions?"
    r"|you\s+are\s+now\s+"
    r"|pretend\s+(?:you\s+are|to\s+be)\s+"
    r"|act\s+as\s+(?:a\s+|an\s+)?"
    r"|new\s+system\s+prompt"
    r"|disregard\s+(?:all\s+)?(?:previous\s+)?instructions?"
    r"|override\s+(?:your\s+)?instructions?",
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Compliance-flag allowlist
# ---------------------------------------------------------------------------
_KNOWN_FLAGS: frozenset[str] = frozenset(
    {
        "customer_data_exposed",
        "data_exposure",
        "gdpr_concern",
        "hipaa_concern",
        "inappropriate_language",
        "missed_verification",
        "missing_disclaimer",
        "pci_concern",
        "privacy_violation",
        "qa_fallback",
        "regulatory_violation",
        "script_deviation",
        "sla_breach",
        "unauthorized_disclosure",
    }
)

# ---------------------------------------------------------------------------
# Audio size (OpenAI Whisper limit: 25 MB)
# ---------------------------------------------------------------------------
_MAX_AUDIO_BYTES: int = 25 * 1024 * 1024


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------


def redact_pii(text: str) -> tuple[str, list[str]]:
    """Redact PII from *text*.

    Returns ``(redacted_text, pii_types_found)`` where *pii_types_found* is a
    deduplicated, ordered list of PII category names that were matched.
    """
    found: list[str] = []
    result = text
    for label, pattern in _PII_PATTERNS:
        if pattern.search(result):
            found.append(label)
            result = pattern.sub(f"[{label.upper()}_REDACTED]", result)
    if found:
        logger.info("[Guardrails] PII redacted | types=%s", found)
    return result, found


def detect_prompt_injection(text: str) -> bool:
    """Return ``True`` (and emit a warning) if *text* includes injection-like patterns."""
    match = _INJECTION_RE.search(text)
    if match:
        logger.warning(
            "[Guardrails] Prompt-injection pattern detected: '%s'",
            match.group().strip(),
        )
        return True
    return False


def validate_compliance_flags(flags: list[str]) -> list[str]:
    """Normalize compliance flags and prefix unknown ones with ``unrecognized_``.

    Normalization: strip, lower-case, replace spaces/dashes with underscores.
    """
    result: list[str] = []
    for flag in flags:
        normalized = flag.strip().lower().replace(" ", "_").replace("-", "_")
        if not normalized:
            continue
        if normalized in _KNOWN_FLAGS:
            result.append(normalized)
        else:
            prefixed = f"unrecognized_{normalized}"
            logger.warning(
                "[Guardrails] Unknown compliance flag '%s' stored as '%s'",
                flag,
                prefixed,
            )
            result.append(prefixed)
    return result


def validate_audio_size(audio_bytes: bytes, session_id: str = "") -> None:
    """Raise ``ValueError`` if *audio_bytes* exceeds the 25 MB Whisper limit."""
    size = len(audio_bytes)
    if size > _MAX_AUDIO_BYTES:
        raise ValueError(
            f"Audio size {size / 1024 / 1024:.1f} MB exceeds the 25 MB limit"
            + (f" [session={session_id}]" if session_id else "")
        )

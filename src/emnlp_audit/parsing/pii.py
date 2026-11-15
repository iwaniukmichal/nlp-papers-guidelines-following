"""Removal of personal data from evaluator inputs (see proposal, Data Statement)."""

import re

EMAIL_PATTERN = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")


def redact_emails(text: str) -> str:
    return EMAIL_PATTERN.sub("[EMAIL_REDACTED]", text)

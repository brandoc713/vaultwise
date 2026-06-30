import re


LONG_NUMBER_RE = re.compile(r"\b(\d{4,})\b")


def redact_description(description: str) -> str:
    return LONG_NUMBER_RE.sub(lambda match: f"****{match.group(1)[-4:]}", description)

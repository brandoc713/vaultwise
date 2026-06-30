from __future__ import annotations

import json
import re
from pathlib import Path

from app.config import get_settings
from app.services.normalization import parse_amount
from app.services.parsers.base import ParsedTransactionCandidate, StatementParser
from app.services.parsers.generic_table_parser import ROW_RE


class LocalPrivateParser(StatementParser):
    name = "local_private_parser"

    def __init__(self, profile_path: Path | None = None) -> None:
        settings = get_settings()
        self.profile_path = profile_path or settings.local_data_dir / "parser_profile.json"

    def parse(self, text: str) -> list[ParsedTransactionCandidate]:
        row_re = ROW_RE
        if self.profile_path.exists():
            profile = json.loads(self.profile_path.read_text(encoding="utf-8"))
            if profile.get("row_regex"):
                row_re = re.compile(profile["row_regex"])

        candidates: list[ParsedTransactionCandidate] = []
        for line in text.splitlines():
            match = row_re.match(line)
            if not match:
                continue
            candidates.append(
                ParsedTransactionCandidate(
                    date_text=match.group("date"),
                    description=match.group("description").strip(),
                    amount=parse_amount(match.group("amount")),
                    source_line=line.strip(),
                )
            )
        return candidates

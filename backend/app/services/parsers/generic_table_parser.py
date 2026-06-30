from __future__ import annotations

import re
from decimal import Decimal

from app.services.normalization import parse_amount
from app.services.parsers.base import ParsedTransactionCandidate, StatementParser


ROW_RE = re.compile(
    r"^\s*(?P<date>(?:\d{4}-\d{2}-\d{2})|(?:\d{1,2}/\d{1,2}(?:/\d{2,4})?))\s+"
    r"(?P<description>.+?)\s+"
    r"(?P<amount>-?\$?\(?\d[\d,]*\.\d{2}\)?)\s*$"
)


class GenericTableParser(StatementParser):
    name = "generic_table_parser"

    def parse(self, text: str) -> list[ParsedTransactionCandidate]:
        candidates: list[ParsedTransactionCandidate] = []
        for line in text.splitlines():
            match = ROW_RE.match(line)
            if not match:
                continue
            try:
                amount = parse_amount(match.group("amount"))
            except ValueError:
                amount = Decimal("0")
                suspicious = True
            else:
                suspicious = False
            candidates.append(
                ParsedTransactionCandidate(
                    date_text=match.group("date"),
                    description=match.group("description").strip(),
                    amount=amount,
                    source_line=line.strip(),
                    suspicious=suspicious,
                )
            )
        return candidates

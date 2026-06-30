from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ParsedTransactionCandidate:
    date_text: str
    description: str
    amount: Decimal
    source_line: str
    suspicious: bool = False


class StatementParser:
    name = "base"

    def parse(self, text: str) -> list[ParsedTransactionCandidate]:
        raise NotImplementedError

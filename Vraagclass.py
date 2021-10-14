
from typing import Dict


class vraag:

    def __init__(self, vraagid, soort, subvragen=None, antwoorden=None, escape=False) -> None:
        self.vraagid = vraagid
        self.soort = soort
        self.antwoorden = antwoorden
        self.subvragen = subvragen
        self.escape = escape

    def __str__(self) -> str:
        if self.soort == "open":
            metzonder = 'met' if self.escape else 'zonder'
            return f"open vraag {metzonder} escape"
        elif self.soort == "tabel":
            return f"tabelvraag met {self.subvragen} subvragen"
        else:
            return f"{self.soort} vraag met {len(self.antwoorden)} antwoorden"

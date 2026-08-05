from dataclasses import dataclass


@dataclass
class Entry:
    name: str
    keywords: list[str] = []

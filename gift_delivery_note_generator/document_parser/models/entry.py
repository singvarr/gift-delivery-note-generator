from dataclasses import dataclass, field


@dataclass(kw_only=True)
class Entry:
    name: str
    keywords: list[str] = field(default_factory=list)

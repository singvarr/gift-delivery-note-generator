from dataclasses import dataclass

@dataclass
class ScannedTextToken:
    page: int
    left: int
    top: int
    width: int
    height: int
    text: str
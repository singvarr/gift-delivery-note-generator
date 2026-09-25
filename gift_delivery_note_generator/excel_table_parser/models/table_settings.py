from dataclasses import dataclass
from pathlib import Path


@dataclass
class TableSettings:
    path: Path
    table_name: str

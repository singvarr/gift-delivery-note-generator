from dataclasses import dataclass


@dataclass(kw_only=True)
class ColumnMapping:
    column: str
    field: str
    is_keyword_field: bool = False

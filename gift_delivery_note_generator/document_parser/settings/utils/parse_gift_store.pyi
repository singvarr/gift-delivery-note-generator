from typing import Iterable, Optional

from ...models.gift_store import GiftStore

def parse_gift_store(text: str, gift_stores: Iterable[GiftStore]) -> Optional[str]: ...
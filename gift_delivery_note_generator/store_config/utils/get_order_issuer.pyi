from typing import Optional
from gift_delivery_note_generator.store_config.constants.gift_category import GiftCategory

def get_order_issuer(text: str) -> Optional[GiftCategory]: ...

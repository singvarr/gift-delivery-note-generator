from gift_delivery_note_generator.delivery_note_renderer import DeliveryNote

from ...models.gift import Gift


def build_gift_details_cell(delivery_note: DeliveryNote, gift: Gift, order_issuer: str) -> str: ...

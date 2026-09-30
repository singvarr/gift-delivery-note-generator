from gift_delivery_note_generator.delivery_note_renderer import DeliveryNote

from ...models.order import OrderRecord


def build_gift_details_cell(
    delivery_note: DeliveryNote,
    entry: OrderRecord,
    order_issuer: str,
) -> str: ...

from gift_delivery_note_generator.models.delivery_note import DeliveryNote
from gift_delivery_note_generator.models.gift import Gift


def build_gift_details_cell(delivery_note: DeliveryNote, gift: Gift) -> str: ...

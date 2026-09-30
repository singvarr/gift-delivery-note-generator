from gift_delivery_note_generator.app import Config

from ...models.delivery_note import DeliveryNote

def build_delivery_note_name(delivery_note: DeliveryNote, config: Config) -> str: ...

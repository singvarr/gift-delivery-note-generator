from gift_delivery_note_generator.models.delivery_note import DeliveryNote


class DeliveryNoteRenderer:
    def __init__(self, delivery_note: DeliveryNote):
        self._delivery_note = delivery_note

    def run(self):
        pass
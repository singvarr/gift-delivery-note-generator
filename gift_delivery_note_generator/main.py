import logging

from gift_delivery_note_generator.app import App

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    app = App()
    app.run()

# gift-delivery-note-generator

A python app that converts order scan in pdf to delivery note. Used for gift store but can be customized and adapted for other businesses.

## Setup

### Prerequisites

Runs on python 3.14.

### Installation

1. Create virtual environment.
2. Create `.env` file using [example](./env-template).
3. Install dependencies from [requirements](./requirements.txt).

### Preparing the project

This project uses list of gifts and gift stores for delivery note generation from excel spreadsheet. Also, you need to provide a template of delivery notes.

The store-specific functions live in gitignored `settings/*.py` files and `.pyi` stubs are committed alongside them. You need to implement them on your own.

## Running the project

You need to pass json with information from scanned document. Use AI capabilities for recognizing structure of your order. **Important**: structure of json should match [Order](./gift_delivery_note_generator/document_parser/models/order.py) model.

Run this command for generation of delivery notes:

```sh
python -m gift_delivery_note_generator.main --order {{PATH_TO_YOUR_JSON}}
```

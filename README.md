# gift-delivery-note-generator

A python app that converts order scan in pdf to delivery note. Used for gift store but can be customized and adapted for other businesses.

## Setup

### Prerequisites

It's assumed that all these dependencies are installed on your OS.

1. python 3.14
2. tesseract OCR engine

### Installation:

1. Install tesseract and add to PATH.
2. Create virtual environment
3. Create `.env` file using [example](./env-template)
4. Install dependencies from [requirements](./requirements.txt)

### Preparing the project

For running of application you need to add order samples in pdf format. Also you need to provide template of output document in `.doc` or `.docx` document.

Also you need to implement handlers and constants stored in `./gift_delivery_note_generator/store_config`. All these items contains sensitive data about stores that's why it's excluded from source version control.

## Application flow

## Production build

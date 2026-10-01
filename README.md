# gift-delivery-note-generator

A python app that converts order scan in pdf to delivery note. Used for gift store but can be customized and adapted for other businesses.

## Setup

### Prerequisites

Runs on python 3.14.

### Installation

1. Create virtual environment
2. Create `.env` file using [example](./env-template)
3. Install dependencies from [requirements](./requirements.txt)

### Preparing the project

This project uses list of gifts and gift stores for delivery note generation from excel spreadsheet. Also, you need to provide a template of delivery notes.

The store-specific functions live in gitignored settings/*.py files and .pyi stubs are committed alongside them. You need to implement them on your own.

import os
import argparse
from pathlib import Path
from json import load

from dacite import from_dict, Config as DaciteConfig
from dotenv import load_dotenv

from gift_delivery_note_generator.excel_table_parser import ExcelTableParser, TableSettings
from gift_delivery_note_generator.excel_table_parser.settings.gift_mappings import GIFT_MAPPINGS
from gift_delivery_note_generator.excel_table_parser.settings.gift_stores import GIFT_STORES
from gift_delivery_note_generator.document_parser import (
    Gift,
    GiftStore,
    GiftCategory,
    Order,
)

from ..constants.env_variables import PATH_ENV_VARIABLES, REQUIRED_ENV_VARIABLES
from ..models.config import Config


class ConfigService:
    def __init__(self) -> None:
        self._parser = argparse.ArgumentParser()

    def _validate_required_keys(self) -> None:
        for variable in REQUIRED_ENV_VARIABLES:
            if variable not in os.environ:
                raise Exception(f"Variable {variable} is missing in .env")

    def _convert_path_fields(self) -> dict[str, Path]:
        result = {}

        for variable in PATH_ENV_VARIABLES:
            path = Path(os.environ[variable])

            if not os.path.exists(path):
                raise Exception(f"{variable} - path doesn't exist")

            result[variable] = path

        return result

    def _parse_order(self) -> Order:
        self._parser.add_argument("--order", type=Path, required=True)
        args = self._parser.parse_args()

        with open(args.order, encoding="utf-8") as data:
            order = load(data)

            return from_dict(
                Order,
                order,
                config=DaciteConfig(strict=True, cast=[GiftCategory]),
            )

    def run(self) -> Config:
        load_dotenv()

        self._validate_required_keys()
        paths = self._convert_path_fields()

        order = self._parse_order()

        settings_table_path = paths["SETTING_TABLE_PATH"]

        gifts_table_settings = TableSettings(
            path=settings_table_path,
            table_name=os.environ["GIFTS_TABLE"],
        )
        gifts_parser = ExcelTableParser(gifts_table_settings, Gift, GIFT_MAPPINGS)
        gifts = gifts_parser.run()

        gift_stores_table_settings = TableSettings(
            path=settings_table_path,
            table_name=os.environ["GIFT_STORES_TABLE"],
        )
        gift_stores_parser = ExcelTableParser(gift_stores_table_settings, GiftStore, GIFT_STORES)
        gift_stores = gift_stores_parser.run()

        return Config(
            template_path=paths["TEMPLATE_PATH"],
            output_path=paths["OUTPUT_PATH"],
            gifts=gifts,
            gift_stores=gift_stores,
            order=order,
        )

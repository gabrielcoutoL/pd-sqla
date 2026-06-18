import logging
from pathlib import Path
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)


class Ingester:
    def __init__(self, data_path: Path):
        self.data_path = data_path

    def ler_csv(
        self,
        nome: str,
        columns: list[str],
        data_types: dict,
        date_columns: Optional[list[str]] = None,
    ) -> pd.DataFrame:
        path = self.data_path / f"{nome}.csv"

        if not path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {path}")

        df = pd.read_csv(
            path, usecols=columns, dtype=data_types, parse_dates=date_columns
        )
        logger.info(f"{nome} {len(df)} registros carregados")

        return df

    def ler_json(
        self,
        nome: str,
        data_types: Optional[dict] = None,
        date_columns: Optional[list[str]] = None,
    ) -> pd.DataFrame:

        path = self.data_path / f"{nome}.json"

        if not path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {path}")

        df = pd.read_json(
            path,
            dtype=data_types,
            convert_dates=date_columns if date_columns else False,
            keep_default_dates=False,
        )
        logger.info(f"{nome} {len(df)} registros carregados")

        return df

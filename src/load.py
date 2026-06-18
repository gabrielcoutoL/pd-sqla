import logging

import pandas as pd
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)


class Loader:
    def __init__(self, engine: Engine):
        self.engine = engine

    def load_to_postgres(self, df: pd.DataFrame, table_name: str) -> None:

        logger.info("Iniciando load do df: %s - %d registros", table_name, len(df))

        df.to_sql(
            name=table_name,
            con=self.engine,
            if_exists="replace",
            index=False,
            chunksize=10_000,
            method="multi",
        )

        logger.info("Load concluido: %s - %d registros", table_name, len(df))

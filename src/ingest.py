import logging
from pathlib import Path
from typing import Optional

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent

PATH_DATA = BASE_DIR.parent / "data" / "raw"

STAGING = BASE_DIR.parent / "data" / "staging"

logger = logging.getLogger(__name__)


class Ingester:
    def __init__(self, data_path: Path = PATH_DATA):
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


if __name__ == "__main__":
    ing = Ingester(data_path=PATH_DATA)

    STAGING.mkdir(parents=True, exist_ok=True)

    dfs = {}

    df_clientes = ing.ler_csv(
        nome="clientes",
        columns=[
            "cliente_id",
            "nome",
            "email",
            "cidade",
            "estado",
            "segmento",
            "data_cadastro",
            "limite_credito",
        ],
        data_types={
            "cliente_id": "int",
            "nome": "str",
            "email": "str",
            "cidade": "str",
            "estado": "str",
            "segmento": "str",
            "limite_credito": "float32",
        },
        date_columns=["data_cadastro"],
    )

    dfs["cliente_stg"] = df_clientes

    df_itens_pedido = ing.ler_csv(
        nome="itens_pedido",
        columns=[
            "item_id",
            "pedido_id",
            "produto_id",
            "quantidade",
            "preco_unitario",
            "desconto",
        ],
        data_types={
            "item_id": "int",
            "pedido_id": "int",
            "produto_id": "int",
            "quantidade": "Int64",
            "preco_unitario": "float32",
            "desconto": "float32",
        },
    )

    dfs["itens_pedido_stg"] = df_itens_pedido

    df_pedidos = ing.ler_json(
        nome="pedidos",
        data_types={
            "pedido_id": "int",
            "cliente_id": "int",
            "status": "str",
            "canal": "str",
        },
        date_columns=["data_pedido"],
    )

    dfs["pedidos_stg"] = df_pedidos

    df_produtos = ing.ler_csv(
        nome="produtos",
        columns=[
            "produto_id",
            "nome_produto",
            "categoria",
            "preco",
            "custo",
            "ativo",
        ],
        data_types={
            "produto_id": "int",
            "nome_produto": "str",
            "categoria": "str",
            "preco": "float32",
            "custo": "float32",
            "ativo": "boolean",
        },
    )

    dfs["produtos_stg"] = df_produtos

    for nome, df in dfs.items():
        df.to_parquet(STAGING / f"{nome}.parquet", index=False)

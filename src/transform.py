import io
import logging
from pathlib import Path
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent

STAGING = BASE_DIR.parent / "data" / "staging"

PROCESSED = BASE_DIR.parent / "data" / "processed"


class Transformer:
    def __init__(self):
        pass

    # --------------------
    # HELPERS
    # --------------------

    def diagnostico(self, df: pd.DataFrame) -> dict:

        logger.info(f"Iniciando diagnóstico para o dataframe: {df}")

        buffer = io.StringIO()

        df.info(memory_usage="deep", buf=buffer)  # info() escreve no buffer

        return {
            "shape": df.shape,
            "info": buffer.getvalue(),
            "nulls": df.isna().sum().to_dict(),
            "uniques": df.nunique().to_dict(),
            "duplicatas": int(df.duplicated().sum()),
            "describe": df.describe().to_string(),
        }

    def remover_nulos(self, df: pd.DataFrame, campos: list[str]) -> pd.DataFrame:

        df_new = df.dropna(subset=campos).reset_index(drop=True)

        logger.info(f"{len(df) - len(df_new)} nulos dropados")

        return df_new

    def drop_duplicates(
        self, df: pd.DataFrame, campos: Optional[list[str]]
    ) -> pd.DataFrame:

        df_new = df.drop_duplicates(subset=campos).reset_index(drop=True)

        logger.info(f"{len(df) - len(df_new)} duplicatas dropadas")

        return df_new

    def to_title_case(self, df: pd.DataFrame, campos: list[str]) -> pd.DataFrame:

        df = df.copy()

        for campo in campos:
            df[campo] = df[campo].str.strip().str.title()

        return df

    # --------------------
    # dim_clientes
    # --------------------

    def transform_clientes(self, df_clientes: pd.DataFrame) -> pd.DataFrame:

        df_clientes = self.remover_nulos(df=df_clientes, campos=["cliente_id"])

        df_clientes = self.drop_duplicates(df=df_clientes, campos=["cliente_id"])

        df_clientes["nome"] = df_clientes["nome"].fillna("Desconhecido")

        df_clientes["limite_credito"] = df_clientes["limite_credito"].fillna(0)

        df_clientes = self.to_title_case(
            df=df_clientes, campos=["nome", "cidade", "segmento"]
        )

        mapa_estados = {"SÃO PAULO": "SP", "MINAS GERAIS": "MG", "RIO DE JANEIRO": "RJ"}
        df_clientes["estado"] = (
            df_clientes["estado"].str.strip().str.upper().replace(mapa_estados)
        )

        df_clientes["email"] = df_clientes["email"].str.lower()

        df_clientes["segmento"] = df_clientes["segmento"].astype("category")

        df_clientes["estado"] = df_clientes["estado"].astype("category")

        return df_clientes

    # --------------------
    # dim_produtos
    # --------------------

    def transform_produtos(self, df_produtos: pd.DataFrame) -> pd.DataFrame:

        df_produtos = self.remover_nulos(df=df_produtos, campos=["produto_id"])

        df_produtos = self.drop_duplicates(df=df_produtos)

        df_produtos = df_produtos.fillna(
            {"nome_produto": "Desconhecido", "categoria": "Desconhecido"}
        )

        df_produtos = self.to_title_case(
            df=df_produtos, campos=["nome_produto", "categoria"]
        )

        df_produtos["categoria"] = df_produtos["categoria"].astype("category")

        return df_produtos

    # --------------------
    # fato_itens_pedido
    # --------------------

    def transform_itens_pedido(self, df_itens_pedido: pd.DataFrame) -> pd.DataFrame:

        df_itens_pedido = self.remover_nulos(
            df=df_itens_pedido, campos=["item_id", "pedido_id", "produto_id"]
        )

        df_itens_pedido = self.drop_duplicates(
            df=df_itens_pedido, campos=["item_id", "pedido_id", "produto_id"]
        )

        df_itens_pedido["desconto"] = df_itens_pedido["desconto"].fillna(0)

        return df_itens_pedido

    # --------------------
    # fato_pedidos
    # --------------------

    def transform_pedidos(self, df_pedidos: pd.DataFrame) -> pd.DataFrame:

        df_pedidos = self.remover_nulos(
            df=df_pedidos, campos=["pedido_id", "cliente_id"]
        )

        df_pedidos = self.drop_duplicates(df=df_pedidos, campos=["pedido_id"])

        df_pedidos = df_pedidos.fillna(
            {"status": "Desconhecido", "canal": "Desconhecido"}
        )

        df_pedidos = self.to_title_case(df=df_pedidos, campos=["status", "canal"])

        df_pedidos["status"] = df_pedidos["status"].astype("category")

        df_pedidos["canal"] = df_pedidos["canal"].astype("category")

        return df_pedidos

import io
import logging

import pandas as pd

logger = logging.getLogger(__name__)


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

        return df.dropna(subset=campos).reset_index(drop=True)

    def drop_duplicates(self, df: pd.DataFrame, campos: list[str]) -> pd.DataFrame:

        return df.drop_duplicates(subset=campos).reset_index(drop=True)

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

        df_clientes = self.to_title_case(
            df=df_clientes, campos=["nome", "cidade", "segmento"]
        )

        mapa_estados = {"SÃO PAULO": "SP", "MINAS GERAIS": "MG", "RIO DE JANEIRO": "RJ"}
        df_clientes["estado"] = (
            df_clientes["estado"].str.strip().str.upper().replace(mapa_estados)
        )

        df_clientes["email"] = df_clientes["email"].str.lower()

        return df_clientes

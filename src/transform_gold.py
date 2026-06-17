import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class GoldTransformer:
    def __init__(self):
        pass

    def enrich_itens_pedido(self, df_itens_pedido, df_produtos):
        return (
            df_itens_pedido.assign(
                receita_bruta=lambda d: d["quantidade"] * d["preco_unitario"],
                receita_liquida=lambda d: d["receita_bruta"] * (1 - d["desconto"]),
            )
            .merge(
                df_produtos[
                    ["produto_id", "nome_produto", "categoria", "preco", "custo"]
                ],
                on="produto_id",
                how="left",
                validate="many_to_one",
            )
            .assign(
                margem=lambda d: d["receita_liquida"] - (d["quantidade"] * d["custo"]),
                faixa_ticket=lambda d: np.select(
                    [d["receita_liquida"] > 200, d["receita_liquida"] >= 100],
                    ["alto", "medio"],
                    default="baixo",
                ),
            )
        )

    def analytical_df(
        self,
        df_enriquecido: pd.DataFrame,
        df_pedidos: pd.DataFrame,
        df_clientes: pd.DataFrame,
    ) -> pd.DataFrame:
        return df_enriquecido.merge(
            df_pedidos[["pedido_id", "cliente_id", "data_pedido", "status", "canal"]],
            on="pedido_id",
            how="left",
            validate="many_to_one",
            indicator="merge_pedidos",
        ).merge(
            df_clientes[["cliente_id", "nome", "cidade", "estado", "segmento"]],
            on="cliente_id",
            how="left",
            validate="many_to_one",
            indicator="merge_clientes",
        )

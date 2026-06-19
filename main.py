import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine

from src.ingest import Ingester
from src.load import Loader
from src.transform import Transformer
from src.transform_gold import GoldTransformer

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

PATH_DATA = Path(os.getenv("DATA_PATH", BASE_DIR.parent / "data" / "raw"))


def orquestrador_principal():

    url = URL.create(
        "postgresql+psycopg2",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=5432,
        database=os.getenv("DB_NAME"),
    )

    engine = create_engine(url=url, pool_size=10, pool_timeout=30, pool_pre_ping=True)

    ing = Ingester(data_path=PATH_DATA)
    trans = Transformer()
    gtrans = GoldTransformer()
    ldr = Loader(engine=engine)

    # --------------------
    # LEITURA E DIAGNÓSTICO
    # --------------------

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
    trans.diagnostico(df_clientes)

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
    trans.diagnostico(df_itens_pedido)

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
    trans.diagnostico(df_pedidos)

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
    trans.diagnostico(df_produtos)

    # --------------------
    # TRANSFORMAÇÕES
    # --------------------

    dim_clientes = trans.transform_clientes(df_clientes)

    dim_produtos = trans.transform_produtos(df_produtos)

    ft_itens_pedido = trans.transform_itens_pedido(df_itens_pedido)

    ft_pedidos = trans.transform_pedidos(df_pedidos)

    # --------------------
    # CAMADA GOLD
    # --------------------

    df_enriquecido = gtrans.enrich_itens_pedido(
        df_itens_pedido=ft_itens_pedido, df_produtos=dim_produtos
    )

    df_analytical = gtrans.analytical_df(
        df_enriquecido=df_enriquecido,
        df_pedidos=ft_pedidos,
        df_clientes=dim_clientes,
    )

    # --------------------
    # LOAD
    # --------------------

    ldr.create_tables()
    ldr.truncate_all()

    ldr.load_to_postgres(df=dim_clientes, table_name="dim_clientes")
    ldr.load_to_postgres(df=dim_produtos, table_name="dim_produtos")
    ldr.load_to_postgres(df=ft_pedidos, table_name="ft_pedidos")
    ldr.load_to_postgres(df=ft_itens_pedido, table_name="ft_itens_pedido")
    ldr.load_to_postgres(df=df_analytical, table_name="analytic_table")


if __name__ == "__main__":
    orquestrador_principal()

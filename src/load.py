import logging

import pandas as pd
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    Numeric,
    String,
    Table,
    text,
)
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)


class Loader:
    def __init__(self, engine: Engine):
        self.engine = engine
        self.metadata = MetaData()

    def create_tables(self):

        clientes = Table(
            "dim_clientes",
            self.metadata,
            Column("cliente_id", Integer, primary_key=True),
            Column("nome", String(120), nullable=False),
            Column("email", String(255), unique=True),
            Column("cidade", String(120)),
            Column("estado", String(2)),
            Column("segmento", String(30)),
            Column("data_cadastro", DateTime),
            Column("limite_credito", Numeric(10, 2)),
        )

        itens_pedido = Table(
            "ft_itens_pedido",
            self.metadata,
            Column("item_id", Integer, primary_key=True),
            Column(
                "pedido_id",
                Integer,
                ForeignKey("ft_pedidos.pedido_id"),
                nullable=False,
            ),
            Column(
                "produto_id",
                Integer,
                ForeignKey("dim_produtos.produto_id"),
                nullable=False,
            ),
            Column("quantidade", Integer),
            Column("preco_unitario", Numeric(10, 2)),
            Column("desconto", Float),
            Index("ix_itsped_pedido", "pedido_id"),
            Index("ix_itsped_produto", "produto_id"),
        )

        pedidos = Table(
            "ft_pedidos",
            self.metadata,
            Column("pedido_id", Integer, primary_key=True),
            Column(
                "cliente_id",
                Integer,
                ForeignKey("dim_clientes.cliente_id"),
                nullable=False,
            ),
            Column("data_pedido", DateTime),
            Column("status", String(30)),
            Column("canal", String(30)),
            Index("ix_pedidos_cliente", "cliente_id"),
        )

        produtos = Table(
            "dim_produtos",
            self.metadata,
            Column("produto_id", Integer, primary_key=True),
            Column("nome_produto", String(120)),
            Column("categoria", String(30)),
            Column("preco", Numeric(10, 2)),
            Column("custo", Numeric(10, 2)),
            Column("ativo", Boolean, default=True),
        )

        self.metadata.create_all(self.engine)

        logger.info("Tabelas criadas / verificadas.")

    def truncate_all(self):
        with self.engine.begin() as conn:
            conn.execute(
                text(
                    "TRUNCATE dim_clientes, dim_produtos, ft_pedidos, ft_itens_pedido "
                    "RESTART IDENTITY CASCADE"
                )
            )

    def load_to_postgres(self, df: pd.DataFrame, table_name: str) -> None:

        logger.info("Iniciando load do df: %s - %d registros", table_name, len(df))

        df.to_sql(
            table_name,
            self.engine,
            if_exists="append",
            index=False,
            chunksize=10_000,
            method="multi",
        )

        logger.info("Load finalizado. Df: %s - %d registros", table_name, len(df))

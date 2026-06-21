import numpy as np
import pandas as pd
import pandera.pandas as pa
from pandera.typing import Series


class BronzeClientes(pa.DataFrameModel):
    cliente_id: Series[int] = pa.Field(gt=0, nullable=True)
    nome: Series[str] = pa.Field(nullable=True)
    email: Series[str] = pa.Field(nullable=True)
    cidade: Series[str] = pa.Field(nullable=True)
    estado: Series[str] = pa.Field(nullable=True)
    segmento: Series[str] = pa.Field(nullable=True)
    data_cadastro: Series[pd.Timestamp] = pa.Field(nullable=True)
    limite_credito: Series[np.float32] = pa.Field(ge=0, nullable=True)

    class Config:
        strict = True
        coerce = True


class SilverClientes(pa.DataFrameModel):
    cliente_id: Series[int] = pa.Field(gt=0, nullable=False, unique=True)
    nome: Series[str] = pa.Field(nullable=False)
    email: Series[str] = pa.Field(nullable=True)
    cidade: Series[str] = pa.Field(nullable=True)
    estado: Series[pd.CategoricalDtype] = pa.Field(nullable=True)
    segmento: Series[pd.CategoricalDtype] = pa.Field(nullable=True)
    data_cadastro: Series[pd.Timestamp] = pa.Field(nullable=True)
    limite_credito: Series[np.float32] = pa.Field(ge=0, nullable=False)

    class Config:
        strict = True
        coerce = True

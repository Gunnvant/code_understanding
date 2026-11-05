from __future__ import annotations

import pandas as pd
import pandera.pandas as pa
from pandera.pandas import Column, DataFrameSchema, Check


raw_schema = DataFrameSchema(
    {
        "id": Column(int, nullable=False),
        "nome": Column(str, nullable=True),
        "email": Column(str, nullable=True),
        "telefone": Column(str, nullable=True),
        "cidade": Column(str, nullable=True),
        "valor_compra": Column(object, nullable=True),
        "data_compra": Column(object, nullable=True),
    },
    strict=False,
    coerce=True,
)


clean_schema = DataFrameSchema(
    {
        "id": Column(int, nullable=False, unique=True),
        "nome": Column(str, nullable=False),
        "email": Column(str, checks=Check.str_matches(r"^[^@]+@[^@]+\.[^@]+$")),
        "telefone": Column(str, nullable=True),
        "cidade": Column(str, nullable=True),
        "valor_compra": Column(float, nullable=True, checks=Check.greater_than_or_equal_to(0)),
        "data_compra": Column("datetime64[ns]", nullable=True),
    },
    strict=False,
    coerce=True,
)


def validate_raw(df: pd.DataFrame) -> pd.DataFrame:
    return raw_schema.validate(df, lazy=True)


def validate_clean(df: pd.DataFrame) -> pd.DataFrame:
    return clean_schema.validate(df, lazy=True)

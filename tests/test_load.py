import pandas as pd
from sqlalchemy import create_engine, text

from etl.load import load


def _read(url, table):
    with create_engine(url, future=True).connect() as conn:
        return pd.read_sql(text(f'SELECT * FROM "{table}"'), conn)


def test_load_sqlite_replace(tmp_path):
    url = f"sqlite:///{tmp_path / 'db.sqlite'}"
    df = pd.DataFrame({"id": [1, 2], "nome": ["a", "b"]})
    stats = load(df, target="sqlite", table="t", mode="replace", connection_url=url)
    assert stats.replaced
    assert len(_read(url, "t")) == 2


def test_load_sqlite_upsert_cdc(tmp_path):
    url = f"sqlite:///{tmp_path / 'db.sqlite'}"
    df1 = pd.DataFrame({"id": [1, 2], "nome": ["a", "b"]})
    load(df1, target="sqlite", table="t", mode="replace", connection_url=url)

    df2 = pd.DataFrame({"id": [1, 2, 3], "nome": ["a", "B_NEW", "c"]})
    stats = load(df2, target="sqlite", table="t", mode="upsert", connection_url=url)
    assert stats.inserted == 1   # id=3
    assert stats.updated == 1    # id=2 mudou
    assert stats.unchanged == 1  # id=1 inalterado

    rows = _read(url, "t").sort_values("id").reset_index(drop=True)
    assert rows.loc[rows["id"] == 2, "nome"].iloc[0] == "B_NEW"
    assert rows.loc[rows["id"] == 3, "nome"].iloc[0] == "c"


def test_load_parquet(tmp_path):
    df = pd.DataFrame({"id": [1, 2], "nome": ["a", "b"]})
    stats = load(df, target="parquet", table="t", mode="replace", parquet_dir=str(tmp_path))
    assert stats.inserted == 2
    assert (tmp_path / "t.parquet").exists()

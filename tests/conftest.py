from pathlib import Path

import pandas as pd
import pytest


SAMPLE_CSV = """id,nome,email,telefone,cidade,valor_compra,data_compra
1,Lucas Mendes,lucas@email.com,14929345525,BAURU,767.0,2024/01/19
2,,juliana@gmail.com,(14) 91320-4752,BAURU,240.55,2024/01/08
3,Lucas Mendes,lucas@yahoo.com.br,,São Paulo,1490.52,2024-01-20
4,maria souza,maria@gmail.com,(14) 95537-4050,CAMPINAS,R$ 221.78,2024/01/28
5,Lucas Mendes,lucas@email.com,14929345525,BAURU,767.0,2024/01/19
6,Carlos Lima,carloslima.email,11999990000,SP,300,2024/02/01
7,Ana Paula,ana@outlier.com,11988888888,RIO,99999.99,2024/02/05
"""


@pytest.fixture
def sample_csv(tmp_path: Path) -> Path:
    p = tmp_path / "clientes_sample.csv"
    p.write_text(SAMPLE_CSV, encoding="utf-8")
    return p


@pytest.fixture
def sample_df() -> pd.DataFrame:
    from io import StringIO

    return pd.read_csv(StringIO(SAMPLE_CSV))

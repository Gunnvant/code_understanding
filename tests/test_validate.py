import pandas as pd
import pytest

from etl.validate import validate_raw


def test_validate_raw_ok(sample_df):
    out = validate_raw(sample_df)
    assert len(out) == len(sample_df)


def test_validate_raw_missing_column():
    df = pd.DataFrame({"id": [1], "nome": ["x"]})
    with pytest.raises(Exception):
        validate_raw(df)

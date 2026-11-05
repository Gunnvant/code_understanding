from etl.extract import extract


def test_extract_csv(sample_csv):
    df = extract(str(sample_csv))
    assert len(df) == 7
    assert "email" in df.columns


def test_extract_rejects_unknown(tmp_path):
    weird = tmp_path / "foo.xyz"
    weird.write_text("")
    import pytest
    with pytest.raises(ValueError):
        extract(str(weird))

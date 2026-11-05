from etl.quality import RejectionReport
from etl.transform import transform


def test_transform_drops_invalid(sample_df):
    report = RejectionReport(run_id="test")
    out = transform(sample_df, report)

    # id=2 nome vazio, id=5 duplicata, id=6 email inválido -> rejeitados
    assert 6 not in set(out["id"])
    assert 5 not in set(out["id"])
    assert 2 not in set(out["id"])
    assert report.total >= 3


def test_transform_normalizes(sample_df):
    report = RejectionReport(run_id="test")
    out = transform(sample_df, report)
    # nome em title case
    assert (out["nome"] == out["nome"].str.title()).all()
    # valor_compra numérico
    assert out["valor_compra"].dtype.kind in ("f", "i")
    # telefone só dígitos ou None
    assert out["telefone"].dropna().str.match(r"^\d+$").all()


def test_transform_keeps_valid(sample_df):
    report = RejectionReport(run_id="test")
    out = transform(sample_df, report)
    assert 1 in set(out["id"])
    assert 4 in set(out["id"])

import pandas as pd

from etl.enrich import detect_anomalies


def test_detect_anomalies_flags_outlier():
    df = pd.DataFrame({"valor_compra": [10, 12, 11, 13, 10, 9, 11, 12, 5000]})
    out = detect_anomalies(df, z_threshold=2.0)
    assert out["is_anomaly"].sum() == 1
    assert out.iloc[-1]["is_anomaly"]


def test_detect_anomalies_small_sample():
    df = pd.DataFrame({"valor_compra": [10, 12]})
    out = detect_anomalies(df)
    assert (out["is_anomaly"] == False).all()  # noqa: E712

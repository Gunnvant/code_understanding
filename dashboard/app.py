from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine, text

from etl.config import settings
from etl.metrics import read_runs


def _url() -> str:
    if settings.etl_target == "postgres":
        return settings.postgres_url
    return settings.sqlite_url


@st.cache_data(ttl=30)
def load_runs() -> pd.DataFrame:
    return read_runs(_url(), limit=200)


@st.cache_data(ttl=30)
def load_table(table: str) -> pd.DataFrame:
    try:
        engine = create_engine(_url(), future=True)
        with engine.connect() as conn:
            return pd.read_sql(text(f'SELECT * FROM "{table}"'), conn)
    except Exception:
        return pd.DataFrame()


def main() -> None:
    st.set_page_config(page_title="ETL Local", layout="wide", page_icon="📊")
    st.title("📊 ETL Local — Dashboard")
    st.caption(f"target={settings.etl_target}  table={settings.etl_table}")

    runs = load_runs()
    df = load_table(settings.etl_table)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total de runs", len(runs))
    c2.metric("Linhas carregadas", len(df))
    if not runs.empty:
        last = runs.iloc[0]
        c3.metric("Último status", last["status"])
        c4.metric("Última duração", f"{float(last['duration_seconds']):.2f}s")

    tab_runs, tab_quality, tab_data, tab_anom = st.tabs(
        ["Runs", "Qualidade", "Dados", "Anomalias"]
    )

    with tab_runs:
        st.subheader("Histórico de execuções")
        if runs.empty:
            st.info("Nenhum run registrado. Rode `etl run` primeiro.")
        else:
            st.dataframe(runs, use_container_width=True)
            fig = px.line(
                runs.sort_values("started_at"),
                x="started_at",
                y="duration_seconds",
                title="Duração por run",
                markers=True,
            )
            st.plotly_chart(fig, use_container_width=True)
            fig2 = px.bar(
                runs.sort_values("started_at"),
                x="started_at",
                y=["rows_in", "rows_out", "rows_rejected"],
                title="Linhas por run",
                barmode="group",
            )
            st.plotly_chart(fig2, use_container_width=True)

    with tab_quality:
        st.subheader("Motivos de rejeição")
        if runs.empty:
            st.info("Nenhum run.")
        else:
            summaries: list[dict] = []
            for _, r in runs.iterrows():
                try:
                    parsed = json.loads(r["rejection_summary"]) if r["rejection_summary"] else {}
                except Exception:
                    parsed = {}
                for reason, count in parsed.items():
                    summaries.append({"run_id": r["run_id"], "reason": reason, "count": count})
            if not summaries:
                st.success("Nenhuma rejeição registrada ✨")
            else:
                summary_df = pd.DataFrame(summaries)
                agg = summary_df.groupby("reason", as_index=False)["count"].sum()
                fig = px.pie(agg, values="count", names="reason", title="Rejeições por motivo")
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(summary_df)

        st.subheader("Relatórios em disco")
        rej_dir = Path(settings.etl_rejected_dir)
        if rej_dir.exists():
            files = sorted(rej_dir.glob("rejected_*.csv"))
            if files:
                pick = st.selectbox("arquivo", [f.name for f in files])
                st.dataframe(pd.read_csv(rej_dir / pick))

    with tab_data:
        st.subheader(f"Tabela `{settings.etl_table}`")
        if df.empty:
            st.info("Sem dados carregados.")
        else:
            st.dataframe(df, use_container_width=True)
            if "cidade" in df.columns:
                top = df["cidade"].value_counts().head(10).reset_index()
                top.columns = ["cidade", "clientes"]
                fig = px.bar(top, x="cidade", y="clientes", title="Top 10 cidades")
                st.plotly_chart(fig, use_container_width=True)
            if "valor_compra" in df.columns:
                fig = px.histogram(df, x="valor_compra", nbins=30, title="Distribuição de valor_compra")
                st.plotly_chart(fig, use_container_width=True)

    with tab_anom:
        st.subheader("Anomalias (is_anomaly=True)")
        if "is_anomaly" not in df.columns:
            st.info("Coluna is_anomaly não encontrada — habilite ETL_DETECT_ANOMALIES.")
        else:
            anomalies = df[df["is_anomaly"] == True]  # noqa: E712
            st.metric("Total de anomalias", len(anomalies))
            st.dataframe(anomalies, use_container_width=True)


if __name__ == "__main__":
    main()

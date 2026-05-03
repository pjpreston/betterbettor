"""
Streamlit GUI for the BB racing database (KAN-28).

Run: ./.venv/bin/streamlit run app.py

Features
- Sidebar date picker + "Load this day's data" button (calls bb_loader.load_csv)
- Data tab: sortable table view of the RACING table with course / horse filters
- Chat tab: Claude Sonnet 4.6 chat that sees the currently filtered rows
"""

from __future__ import annotations

import os
import sqlite3
from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

import bb_loader
from bb_schema import DB_PATH, create_schema

load_dotenv()

CSV_DIR = Path("/home/pete/projects/BB/DATA/RP/DATA/region/all/all")
DEFAULT_DATE = date(2026, 4, 28)
CLAUDE_MODEL = "claude-sonnet-4-6"
MAX_ROWS_TO_LLM = 500


def _csv_path_for(d: date) -> Path:
    return CSV_DIR / f"{d:%Y_%m_%d}.csv"


def _fetch_rows(date_filter: date | None) -> pd.DataFrame:
    create_schema(DB_PATH)
    con = sqlite3.connect(DB_PATH)
    try:
        if date_filter is None:
            return pd.read_sql_query("SELECT * FROM RACING ORDER BY date, course, off, num", con)
        return pd.read_sql_query(
            "SELECT * FROM RACING WHERE date = ? ORDER BY course, off, num",
            con,
            params=(date_filter.strftime("%Y-%m-%d"),),
        )
    finally:
        con.close()


def _build_system_prompt(df: pd.DataFrame, label: str) -> str:
    if df.empty:
        body = "(no rows)"
    else:
        capped = df.head(MAX_ROWS_TO_LLM)
        body = capped.to_csv(index=False)
        if len(df) > MAX_ROWS_TO_LLM:
            body += f"\n(showing first {MAX_ROWS_TO_LLM} of {len(df)} rows)\n"
    return (
        "You are a horse racing analysis assistant. You have access to the following "
        f"rows from the RACING table ({label}), in CSV format. Each row is one horse's "
        "run in one race. Answer the user's questions using only this data. If the data "
        "does not contain the answer, say so plainly.\n\n"
        f"{body}"
    )


@st.cache_resource
def _anthropic_client():
    from anthropic import Anthropic

    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    return Anthropic()


def _chat_call(system_prompt: str, history: list[dict]) -> str:
    client = _anthropic_client()
    if client is None:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Add it to /home/pete/projects/BB/.env "
            "and restart the app."
        )
    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=2048,
        system=[{"type": "text", "text": system_prompt, "cache_control": {"type": "ephemeral"}}],
        messages=history,
    )
    return "".join(block.text for block in response.content if block.type == "text")


def _render_sidebar() -> tuple[date, bool]:
    st.sidebar.header("BetterBettor")
    selected_date = st.sidebar.date_input("Date", value=DEFAULT_DATE)

    if st.sidebar.button("Load this day's data", width="stretch"):
        csv_path = _csv_path_for(selected_date)
        if not csv_path.exists():
            st.sidebar.error(f"No CSV found at {csv_path}")
        else:
            try:
                n = bb_loader.load_csv(csv_path)
                st.sidebar.success(f"Loaded {n} rows from {csv_path.name}")
            except Exception as exc:
                st.sidebar.error(f"Load failed: {exc}")

    show_all = st.sidebar.checkbox("Show all dates", value=False)
    return selected_date, show_all


def _render_data_tab(df: pd.DataFrame, label: str) -> pd.DataFrame:
    st.subheader(f"RACING — {label}")

    if df.empty:
        st.info("No rows. Use the sidebar to load a day's data.")
        return df

    courses = sorted(c for c in df["course"].dropna().unique())
    selected_courses = st.multiselect("Course", courses)
    horse_query = st.text_input("Horse name contains", "").strip()

    view = df
    if selected_courses:
        view = view[view["course"].isin(selected_courses)]
    if horse_query:
        view = view[view["horse"].str.contains(horse_query, case=False, na=False)]

    c1, c2, c3 = st.columns(3)
    c1.metric("Rows", len(view))
    c2.metric("Courses", view["course"].nunique())
    c3.metric("Horses", view["horse"].nunique())

    st.dataframe(view, width="stretch", height=600)
    return view


def _render_chat_tab(view: pd.DataFrame, label: str) -> None:
    st.subheader("Chat")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    cols = st.columns([1, 5])
    if cols[0].button("Clear chat"):
        st.session_state.chat_history = []
        st.rerun()
    cols[1].caption(
        f"Claude sees {min(len(view), MAX_ROWS_TO_LLM)} of {len(view)} currently filtered rows ({label})."
    )

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask about the data…")
    if not user_input:
        return

    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    system_prompt = _build_system_prompt(view, label)
    try:
        with st.chat_message("assistant"), st.spinner("Thinking…"):
            reply = _chat_call(system_prompt, st.session_state.chat_history)
            st.markdown(reply)
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
    except Exception as exc:
        st.session_state.chat_history.pop()
        st.error(str(exc))


def main() -> None:
    st.set_page_config(page_title="BetterBettor", layout="wide")

    selected_date, show_all = _render_sidebar()
    label = "all dates" if show_all else selected_date.strftime("%Y-%m-%d")
    df = _fetch_rows(None if show_all else selected_date)

    data_tab, chat_tab = st.tabs(["Data", "Chat"])
    with data_tab:
        view = _render_data_tab(df, label)
    with chat_tab:
        _render_chat_tab(view, label)


if __name__ == "__main__":
    main()

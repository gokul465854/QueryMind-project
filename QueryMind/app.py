import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

from clarification.detector import detect_ambiguity
from core.orchestrator import QueryMindOrchestrator
from database.connection import validate_sqlite_bytes
from history.manager import init_history, add_history, get_history
from schema.inspector import inspect_database
from visualization.charts import suggest_chart

st.set_page_config(page_title="QueryMind", page_icon="🧠", layout="wide")
st.title("🧠 QueryMind")
st.caption("AI-Powered Database Assistant · Schema-aware Text-to-SQL with intelligent clarification")

init_history()
if "db_path" not in st.session_state:
    st.session_state.db_path = None
if "clarification_state" not in st.session_state:
    st.session_state.clarification_state = None

with st.sidebar:
    st.header("Database")
    uploaded = st.file_uploader("Upload a SQLite database", type=["db", "sqlite", "sqlite3"])
    if uploaded is not None:
        try:
            db_path = validate_sqlite_bytes(uploaded.getvalue(), uploaded.name)
            st.session_state.db_path = str(db_path)
            st.success(f"Loaded: {uploaded.name}")
        except Exception as exc:
            st.error(f"Could not load this database: {exc}")
    if st.session_state.db_path and os.path.exists(st.session_state.db_path):
        try:
            schema = inspect_database(st.session_state.db_path)
            st.metric("Tables", len(schema["tables"]))
            for table_name, info in schema["tables"].items():
                with st.expander(f"{table_name} ({info['row_count']} rows)"):
                    st.write(info["columns"])
                    if info["sample_rows"]:
                        st.dataframe(pd.DataFrame(info["sample_rows"]), use_container_width=True)
        except Exception as exc:
            st.warning(f"Database inspection failed: {exc}")
    st.divider()
    st.subheader("Recent query history")
    for item in get_history(limit=8):
        st.caption(f"{item['timestamp']} · {item['status']}")
        st.write(item["question"])

if not st.session_state.db_path:
    st.info("Upload a SQLite database to begin, or use the included demo database.")
    demo = st.button("Use demo university database")
    if demo:
        st.session_state.db_path = str((Path(__file__).parent / "database" / "demo_university.db").resolve())
        st.rerun()
    st.stop()

schema = inspect_database(st.session_state.db_path)
with st.expander("Database schema and relationships", expanded=False):
    st.code(schema["schema_text"], language="text")
    st.write("Foreign-key relationships")
    st.json(schema["relationships"])

question = st.text_area("Ask your database", placeholder="Example: Show the top students by marks", height=90)
col1, col2 = st.columns([1, 4])
with col1:
    run_query = st.button("Ask QueryMind", type="primary", use_container_width=True)
with col2:
    st.caption("Only read-only SELECT queries are eligible for execution.")

if run_query and question.strip():
    ambiguity = detect_ambiguity(question, schema)
    if ambiguity["needs_clarification"]:
        st.session_state.clarification_state = {
            "original_question": question.strip(),
            "question": ambiguity["question"],
            "reason": ambiguity["reason"],
            "answers": [],
        }
    else:
        st.session_state.clarification_state = {
            "original_question": question.strip(),
            "question": "",
            "reason": "",
            "answers": [],
        }
        st.session_state.run_resolved_query = True

if st.session_state.clarification_state:
    state = st.session_state.clarification_state
    if state.get("question"):
        st.warning(state["reason"])
        st.write(state["question"])
        answer = st.text_input("Your clarification", key="clarification_answer")
        if st.button("Submit clarification"):
            if answer.strip():
                state["answers"].append({"question": state["question"], "answer": answer.strip()})
                combined = state["original_question"] + " Clarification: " + "; ".join(
                    f"{x['question']} {x['answer']}" for x in state["answers"]
                )
                next_ambiguity = detect_ambiguity(combined, schema)
                if next_ambiguity["needs_clarification"] and len(state["answers"]) < 3:
                    state["question"] = next_ambiguity["question"]
                    state["reason"] = next_ambiguity["reason"]
                else:
                    state["question"] = ""
                    state["resolved_question"] = combined
                    st.session_state.run_resolved_query = True
                st.rerun()
    elif st.session_state.get("run_resolved_query"):
        resolved_question = state.get("resolved_question", state["original_question"])
        st.session_state.run_resolved_query = False
        try:
            orchestrator = QueryMindOrchestrator(st.session_state.db_path)
            outcome = orchestrator.run(resolved_question)
            add_history(
                question=state["original_question"],
                clarification=state.get("answers", []),
                sql=outcome.get("sql", ""),
                status=outcome["status"],
                execution_time=outcome.get("execution_time", 0.0),
                retries=outcome.get("retries", 0),
            )
            st.subheader("Query understanding")
            st.write(outcome.get("intent", "Database query"))
            with st.expander("Explain query"):
                st.write(outcome.get("explanation", ""))
                st.write("Tables used:", ", ".join(outcome.get("tables_used", [])))
                st.write("Columns used:", ", ".join(outcome.get("columns_used", [])))
            st.subheader("Generated SQL")
            st.code(outcome.get("sql", ""), language="sql")
            st.write("Validation:", outcome.get("validation_message", "Not available"))
            st.write("Execution status:", outcome["status"])
            if outcome["status"] == "success":
                df = outcome["dataframe"]
                st.dataframe(df, use_container_width=True)
                st.subheader("Result explanation")
                st.write(outcome.get("summary", "Query completed successfully."))
                chart = suggest_chart(df)
                if chart:
                    st.subheader("Suggested visualization")
                    chart_type, x_col, y_col = chart
                    view = st.radio("View", ["Table", "Chart", "SQL", "Explanation"], horizontal=True)
                    if view == "Chart":
                        if chart_type == "line":
                            st.plotly_chart(__import__("plotly.express", fromlist=["line"]).line(df, x=x_col, y=y_col), use_container_width=True)
                        else:
                            st.plotly_chart(__import__("plotly.express", fromlist=["bar"]).bar(df, x=x_col, y=y_col), use_container_width=True)
                    elif view == "SQL":
                        st.code(outcome.get("sql", ""), language="sql")
                    elif view == "Explanation":
                        st.write(outcome.get("summary", ""))
            else:
                st.error(outcome.get("message", "Query could not be completed."))
        except Exception as exc:
            st.error(f"QueryMind could not complete the request. Check the database and LLM configuration. Details: {exc}")

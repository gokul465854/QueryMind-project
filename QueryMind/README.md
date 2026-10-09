# QueryMind — AI-Powered Database Assistant

QueryMind is a Python and Streamlit project that translates natural-language questions into read-only SQLite queries using an LLM. Its central feature is an intelligent clarification workflow that asks follow-up questions when a request is underspecified.

> This is a phased starter implementation. Review the known limitations below before presenting it as a complete system.

## Features in this starter
- Streamlit interface and SQLite database upload
- Automatic table, column, primary-key, foreign-key, row-count, and sample-row inspection
- LLM-based SQL generation using OpenRouter-compatible or OpenAI-compatible API configuration
- Deterministic initial ambiguity checks
- SQLGlot AST parsing and SELECT-only validation
- Read-only SQLite connection and SQLite authorizer
- Result table, basic result summary, chart suggestion, and query history
- Initial unit tests and evaluation metric helpers

## Not yet complete
- The evaluation dataset currently contains 5 examples, not the target 50
- SQL self-correction is scaffolded but not integrated into orchestration
- Clarification detection is a deterministic heuristic, not a full LLM structured-intent analysis
- Validation checks table names, but comprehensive column resolution and join-policy enforcement need more work
- Timeouts and resource limits require additional adversarial testing
- Result explanation is deliberately simple and does not use an LLM
- Uploaded database files are stored in a temporary location; production-grade lifecycle cleanup is not yet implemented
- No performance or accuracy claims are made; metrics must be measured from real experiments

## Requirements
- Python 3.10+
- An LLM API key (OpenRouter or compatible provider)
- A SQLite `.db`, `.sqlite`, or `.sqlite3` file

## Setup (Windows PowerShell)
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```
Edit `.env` and add your API key. The app does not automatically load `.env` unless `python-dotenv` is loaded, so either export the variables in your shell or add `load_dotenv()` near the top of `app.py` in the next setup phase.

```powershell
python -m unittest discover -s tests -v
streamlit run app.py
```

## Workflow
1. Upload a SQLite database.
2. Inspect the schema shown in the sidebar and schema panel.
3. Ask a natural-language question.
4. Answer a clarification question if prompted.
5. Review generated SQL and validation status.
6. Inspect result rows and suggested visualization.

## Security notes
- Generated SQL is treated as untrusted.
- SQLGlot validation is followed by read-only SQLite execution and a SQLite authorizer.
- Never expose or commit API keys.
- Do not use untrusted databases containing sensitive data for demonstrations.
- This is a student-project starter, not a hardened multi-user service.

## Project structure
```text
QueryMind/
├── app.py
├── core/
├── llm/
├── clarification/
├── schema/
├── sql/
├── result/
├── visualization/
├── history/
├── evaluation/
├── database/
├── tests/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Evaluation plan
Build a reviewed dataset of at least 50 questions with expected SQL/result criteria and ambiguity labels. Measure SQL generation accuracy, execution accuracy, clarification precision/recall/F1, self-correction success, latency, clarification turns, and failure rate. Report only measurements obtained by running the evaluation.

## Future phases
1. Harden schema-aware validation and safe execution.
2. Add structured intent analysis and robust multi-turn clarification.
3. Integrate bounded SQL self-correction with re-validation on every retry.
4. Expand tests and build the 50-case evaluation suite.
5. Compare basic Text-to-SQL against clarification and self-correction configurations.
6. Complete documentation and demonstration scripts.

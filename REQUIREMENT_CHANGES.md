# Requirement Changes and Install Notes

This file documents the dependency changes made while installing RetailWise AI locally.

## Backend Requirement Changes

Updated `backend/requirements.txt` and the tech stack table in `full_flow.md`:

| Package | Previous | Current | Reason |
|---------|----------|---------|--------|
| `langchain-google-genai` | `1.0.6` | `1.0.10` | `1.0.6` requires `google-generativeai<0.6.0`, which conflicts with the spec pin `google-generativeai==0.7.2`. Version `1.0.10` stays in the same adapter line and resolves with Gemini SDK `0.7.2`. |
| `llama-index` | `0.10.40` | replaced with `llama-index-core==0.10.68.post1` | The `llama-index` meta package pulls OpenAI-specific packages. The project rule is Gemini everywhere, so we install LlamaIndex core plus Chroma integration only. Gemini calls should use `google-generativeai` or `langchain-google-genai`. |
| `pydantic` | `2.7.1` | `2.7.4` | Required by the resolved LangChain core dependency on the current Python runtime. |

No `openai` or `anthropic` package is installed in the backend virtual environment.

## Local Python Setup

The machine only had Python `3.12.7`. Installing the original dependency set on Python 3.12 failed because `chromadb==0.5.0` depends on `chroma-hnswlib==0.7.3`, which tried to compile with Microsoft C++ Build Tools.

To avoid changing the system Python install, a project-local Python `3.11.9` package was downloaded under:

```text
.tools/python311_pkg/tools/python.exe
```

The backend virtual environment was created from that local interpreter:

```powershell
cd backend
..\.tools\python311_pkg\tools\python.exe -m venv .venv311
.\.venv311\Scripts\python.exe -m pip install -r requirements.txt
```

Both `.tools/` and `.venv311/` are ignored in `.gitignore`.

## Frontend Install

Frontend dependencies were installed inside the `frontend` folder:

```powershell
cd frontend
npm.cmd install
```

`npm.cmd` was used because PowerShell blocked the `npm.ps1` script under the current execution policy.

The install created:

```text
frontend/node_modules/
frontend/package-lock.json
```

NPM reported two audit issues. No automatic `npm audit fix --force` was run because it can introduce breaking dependency changes.

# Copilot Instructions

## Project overview
This is a small FastAPI teaching app ("Mergington High School Activities API") used for a GitHub Skills exercise. It has no database — all data lives in an in-memory Python dict — and no test suite currently exists.

## Running the app
```bash
pip install -r requirements.txt
cd src
uvicorn app:app --reload
```
- API docs: http://localhost:8000/docs
- Frontend: http://localhost:8000/ (redirects to `/static/index.html`)

Note: `app.py` has no `if __name__ == "__main__"` block, so use `uvicorn` (not `python app.py`) to run it.

## Testing
`pytest.ini` sets `pythonpath = .`, and `httpx` is in `requirements.txt` (used for FastAPI `TestClient`), but no test files exist yet. When adding tests, place them so pytest's rootdir-relative imports work (e.g. `from src.app import app` or add a conftest), and run with:
```bash
pytest                  # full suite
pytest path/to/test_file.py::test_name   # single test
```

## Architecture
- `src/app.py` — single-file FastAPI app. All routes, the in-memory `activities` dict, and static file mounting live here. There is no separate models/routes/db layer — keep changes consistent with this single-module style unless refactoring is explicitly requested.
- `src/static/` — vanilla JS/HTML/CSS frontend (`index.html`, `app.js`, `styles.css`), served via FastAPI's `StaticFiles` mount at `/static`. `app.js` talks to the backend purely via `fetch()` calls to `/activities` (GET) and `/activities/{name}/signup?email=...` (POST) — no build step or framework.
- Activity identity is the **activity name string** (used as dict key and in URLs); student identity is their **email string** appended to `participants` lists. There are no separate ID fields.
- Data resets on every server restart (in-memory only, no persistence layer).

## Conventions
- Keep the API and data model intentionally simple/flat, matching `src/README.md`'s documented data model (Activities keyed by name; Students keyed by email) — avoid introducing ORMs, external databases, or auth unless the task requires it.
- Frontend fetch calls use `encodeURIComponent` for activity name and email in the signup URL — preserve this when modifying `app.js`.
- `.github/workflows/` and `.github/steps/` drive the GitHub Skills exercise itself (issue-based progression); they are course infrastructure, not application code — avoid modifying them unless the task is specifically about the exercise flow.

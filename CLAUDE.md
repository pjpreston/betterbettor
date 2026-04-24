# BetterBettor — Claude Code Guidance

## Project Overview
Python application to assist with horse race betting. Uses theracingapi.com to extract racing data into JSON files.

## Environment Setup

```bash
uv venv
uv pip install -r requirements.txt
```

Python version: 3.13 (managed via `.venv/`). Always use `.venv/bin/python` to run scripts.

## Credentials
API credentials are loaded via `python-dotenv` from a `.env` file in the project root (not committed to git):

```
RACING_API_KEY=your_username
RACING_API_PWD=your_password
```

## Key Files
- `racing_api.py` — one function per theracingapi.com endpoint; each function saves its response as JSON to `/home/pete/projects/BB/DATA/`
- `test_racing_api.py` — integration tests that hit the REAL API (no mocks); tests are skipped if credentials are not set

## Running Tests
```bash
.venv/bin/python -m unittest test_racing_api.py -v
```

Tests make live API calls. They will take ~35–40 seconds due to rate-limit delays (1.1s between calls). Some endpoints require a paid plan — those tests will fail with 401 if the plan doesn't cover them.

## Data Output
All API responses are saved as JSON files in `/home/pete/projects/BB/DATA/` (outside the repo). This directory is created automatically by `racing_api.py` on import.

## API Plan Coverage
The free plan covers:
- `/v1/courses/regions` and `/v1/courses`
- `/v1/racecards` and `/v1/results`

Standard/Pro plan required for:
- All `search_*` functions (horses, jockeys, trainers, owners, sires, dams, damsires)
- All `*_results` and `*_analysis_*` functions

## Patterns & Conventions
- All API functions follow the same pattern: `_get(path, params)` → `_save(filename, data)` → `return data`
- Filenames for saved JSON are derived from the function arguments (e.g. `horse_{horse_id}_results.json`)
- Never hardcode credentials — always use env vars via `.env`
- Add one function per API endpoint; keep them thin (call `_get`, call `_save`, return)

## Implementing changes
- Jira access via MCP is needed in order to access requirements. Jira URL is https://londoncoders.atlassian.net
- all code should be stored in github in the repository with URL https://github.com/pjpreston/betterbettor
- each demand should be implemented in its own github branch

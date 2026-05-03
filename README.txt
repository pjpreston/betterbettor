BetterBettor is an application to assist betting on the horses

The GUI (uses sonnet as the LLM)
----------------------------------------------------------------
From the repo root (/home/pete/projects/BB/betterbettor):

.venv/bin/streamlit run app.py
Then open http://localhost:8501 in your browser.

Prerequisites (one-time):

ANTHROPIC_API_KEY set in /home/pete/projects/BB/.env (already done)
Dependencies installed: uv pip install -r requirements.txt
Using it:

Sidebar → pick a date → click Load this day's data (loads the matching CSV from /home/pete/projects/BB/DATA/RP/DATA/region/all/all/)
Data tab — filter by course / horse name, see metrics

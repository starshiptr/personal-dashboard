# Personal Dashboard

A self-hosted daily very minimalist tracker for spending, fitness, and tasks — built with Streamlit + SQLite, deployed as an always-on service reachable from anywhere over Tailscale. Meant to work with an Obsidian Vault 

## Features
- **Spending** — log expenses, month-to-date metric vs budget, by-category bar chart, editable table, month-end export.
- **Fitness** — per-exercise progressive-overload tracker (long-format data) with a weight-over-time line chart.
- **Tasks** — renders a live Markdown task board synced from an Obsidian vault.
- Inline **edit/delete** on data tables, **month-end Markdown export** back to the vault, gruvbox theme.

## Stack
Python · Streamlit (UI) · SQLite (storage) · pandas (aggregation)

## Architecture — "two memories"
The app is the **daily scratchpad**: granular spending/fitness entries live in a local SQLite database (`dashboard.db`). The **Obsidian vault** is the long-term record. At month-end the app exports a Markdown summary into the vault — so daily data and the permanent record stay cleanly separated, with no double-entry.

## Run locally
```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py

Configuration

Set VAULT_ROOT to the folder holding your todolist/ and finance/ directories (used by the Tasks tab and exports):
export VAULT_ROOT=/path/to/vault        # Windows: setx VAULT_ROOT "C:\path\to\vault"

Deployment (always-on, access anywhere)

Runs 24/7 on a headless Ubuntu Server VM:
- systemd service keeps it running, auto-restarts on failure, starts at boot.
- Tailscale provides private, encrypted access from any device — no public exposure.
- Syncthing mirrors the Obsidian vault to the server so the Tasks tab and exports work remotely.

dashboard.db and .venv/ are gitignored — personal data never leaves the host.
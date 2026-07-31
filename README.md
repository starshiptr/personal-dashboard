<img width="1866" height="1078" alt="image" src="https://github.com/user-attachments/assets/1b9ba8b5-e199-4aab-94f9-71ed60c16c4a" />
<img width="1878" height="943" alt="image" src="https://github.com/user-attachments/assets/a14ef2b2-b925-4756-be60-66831d0a4e26" />

# Personal Dashboard

A minimalist self hosted tracker for spending, fitness, and tasks. Built with Streamlit and SQLite, it runs as an always on service reachable from any device over Tailscale, and it reads and writes a companion Obsidian vault.

## Features

* **Spending:** log expenses, see month to date spend against budget, a category bar chart, an editable table, and a monthly export.
* **Fitness:** a progressive overload tracker per exercise, with a weight over time line chart.
* **Tasks:** renders a live task board from a markdown file in an Obsidian vault.
* Inline edit and delete on the data tables, a gruvbox theme, and a monthly markdown export back into the vault.

## Stack

Python, Streamlit for the UI, SQLite for storage, pandas for aggregation.

## Architecture: two memories

The app is the daily scratchpad. Granular spending and fitness entries live in a local SQLite database (`dashboard.db`). The Obsidian vault is the long term record. At the end of each month the app exports a markdown summary into the vault, so the daily data and the permanent record stay cleanly separated with no double entry.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Configuration

Set `VAULT_ROOT` to the folder that holds your `todolist/` and `finance/` directories. The Tasks tab and the exports read from it.

```bash
export VAULT_ROOT=/path/to/vault        # Windows: setx VAULT_ROOT "C:\path\to\vault"
```

## Deployment

Runs continuously on a headless Ubuntu Server VM:

* A systemd service keeps it running, restarts it on failure, and starts it at boot.
* Tailscale gives private, encrypted access from any device, with no public exposure.
* Syncthing mirrors the Obsidian vault to the server so the Tasks tab and exports work remotely.

`dashboard.db` and `.venv/` are gitignored, so personal data never leaves the host.

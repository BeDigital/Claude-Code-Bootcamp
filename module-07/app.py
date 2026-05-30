#!/usr/bin/env python3
"""Dashboard — Flask + Jinja, static sample data, no database."""

from flask import Flask, render_template

app = Flask(__name__)

ROWS = [
    {"id": 1, "name": "Alpha Project",  "status": "Active",   "owner": "Alice",   "updated": "2026-05-28"},
    {"id": 2, "name": "Beta Release",   "status": "Pending",  "owner": "Bob",     "updated": "2026-05-27"},
    {"id": 3, "name": "Gamma Rollout",  "status": "Active",   "owner": "Carol",   "updated": "2026-05-26"},
    {"id": 4, "name": "Delta Audit",    "status": "Blocked",  "owner": "Dan",     "updated": "2026-05-25"},
    {"id": 5, "name": "Epsilon Review", "status": "Complete", "owner": "Eve",     "updated": "2026-05-24"},
]

KPIS = [
    {"label": "KPI 1", "title": "Total Projects", "value": "142",  "delta": "+12%"},
    {"label": "KPI 2", "title": "Active Items",   "value": "38",   "delta": "+4%"},
    {"label": "KPI 3", "title": "Completed",      "value": "1,204","delta": "+8%"},
]

NAV = ["Overview", "Notes", "Tasks", "Reports", "Settings"]


@app.route("/")
def index():
    """Render the main dashboard page."""
    return render_template("index.html", rows=ROWS, kpis=KPIS, nav=NAV, version="v1.0.0")


if __name__ == "__main__":
    app.run(debug=True, port=5050)

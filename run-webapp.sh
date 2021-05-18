#!/bin/bash

cd backend/

# Start CSV import file listener as a background process.
python3 ./csv_import.py /personal-budget/data &

# Start API.
uwsgi --http :5000 -s /tmp/personal-budget.sock --manage-script-name --mount /=api:app --pyargv "/personal-budget/data"

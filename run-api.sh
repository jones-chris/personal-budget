#!/bin/bash

#python3 ./backend/api.py ./data
#uwsgi --http :5000 -s /tmp/personal-budget.sock --manage-script-name --mount /=backend.api:app --pyargv "/home/pc/Documents/budget"
uwsgi --http :5000 -s /tmp/personal-budget.sock --manage-script-name --mount /pb=backend.api:app --pyargv "./data"
#uwsgi --socket 0.0.0.0:5000 --protocol=http -w  --mount /=backend.api:app --pyargv "./data"
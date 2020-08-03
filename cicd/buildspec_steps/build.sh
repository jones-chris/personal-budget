#!/bin/bash

mkdir package/
python3 -m pip install -r personal_budget/requirements.txt --target package/ --index-url=https://pypi.python.org/simple
cd package/
zip -r9 ../personal-budget.zip  .
cd ../personal_budget/
zip -g ../personal-budget.zip main.py

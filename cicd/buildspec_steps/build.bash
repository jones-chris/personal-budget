#!/bin/bash

PROJECT_VERSION=$1
ZIP_FILE_NAME="personal-budget-$PROJECT_VERSION.zip"

mkdir package/
python3 -m pip install -r personal_budget/requirements.txt --target package/ --index-url=https://pypi.python.org/simple
cd package/ || exit 1
zip -r9 ../"$ZIP_FILE_NAME"  .
cd ../personal_budget/ || exit 1
zip -g ../"$ZIP_FILE_NAME" main.py

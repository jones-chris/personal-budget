#!/bin/bash

if [ "$APP" = "" ]; then
  echo "APP is empty.  Set the APP environment variable using the -e option when starting the container."
  exit 1
elif [ "$APP" = "webapp" ]; then
  echo "Running the web app (the API and UI)"
  ./run-webapp.sh
elif [ "$APP" = "api-only" ]; then
  echo "Running the API only"
  ./run-api.sh
elif [ "$APP" = "ofx-import" ]; then
  echo "Running the OFX import"
  ./run-ofx-import.sh
elif [ "$APP" = "csv-import" ]; then
  echo "Running the CSV import"
  ./run-csv-import.sh
else
  echo "$APP not recognized"
  exit 1
fi



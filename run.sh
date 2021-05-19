#!/bin/bash

if [ "$APP" = "" ]; then
  echo "APP is empty.  Set the APP environment variable using the -e option when starting the container."
  exit 1
elif [ "$APP" = "webapp" ]; then
  echo "Running the web app (the API and UI)"
  ./run-webapp.sh
elif [ "$APP" = "ofx-import" ]; then
  echo "Running the OFX import"
  ./run-ofx-import.sh
else
  echo "$APP not recognized"
  exit 1
fi



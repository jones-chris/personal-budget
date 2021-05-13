#!/bin/bash

# Run the API in the background.
./run-api.sh &
status=$?
if [ $status -ne 0 ]; then
  echo "Failed to start the API: $status"
  exit $status
fi

# Run the UI in the background.
#./run-ui.sh &
#status=$?
#if [ $status -ne 0 ]; then
#  echo "Failed to start the UI: $status"
#  exit $status
#fi

while :; do
  sleep 100
done

#while sleep 60; do
#  ps aux | grep run-api | grep -q -v grep
#  API_STATUS=$?
#  ps aux | grep run-ui | grep -q -v grep
#  UI_STATUS=$?
#  # If the greps above find anything, they exit with 0 status
#  # If they are not both 0, then something is wrong
#  if [ $API_STATUS -ne 0 -o $UI_STATUS -ne 0 ]; then
#    echo "One of the processes has already exited."
#    exit 1
#  fi
#done
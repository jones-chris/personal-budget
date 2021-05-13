#!/bin/bash

# Run a local HTTP server on port 3000 serving the assets in the /build directory.
python3 -m http.server 3000 --directory ./ui/

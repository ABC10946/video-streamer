#!/usr/bin/env bash
set -euo pipefail

# Start streamer.sh in background
bash /app/streamer.sh &
STREAMER_PID=$!

cleanup() {
  echo "Stopping children..."
  kill -TERM "$STREAMER_PID" 2>/dev/null || true
  kill -TERM "$PY_PID" 2>/dev/null || true
  wait "$STREAMER_PID" 2>/dev/null || true
  wait "$PY_PID" 2>/dev/null || true
  exit 0
}

trap cleanup TERM INT

# Start our authenticated HTTP server in background and keep PID
python3 /app/main.py &
PY_PID=$!

# Wait for either to exit, then run cleanup
wait -n
cleanup

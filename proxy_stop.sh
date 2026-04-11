#!/bin/bash
# Stop the mitmproxy token tracker and restore macOS proxy settings

PIDFILE="/tmp/pathless-mitm.pid"

if [ -f "$PIDFILE" ]; then
  PID=$(cat "$PIDFILE")
  if kill -0 "$PID" 2>/dev/null; then
    kill "$PID"
    echo "Stopped proxy (PID $PID)"
  fi
  rm -f "$PIDFILE"
else
  echo "No proxy running."
fi

echo "Restoring macOS proxy settings..."
networksetup -setwebproxystate Wi-Fi off
networksetup -setsecurewebproxystate Wi-Fi off

echo "Done. Token tracking stopped."

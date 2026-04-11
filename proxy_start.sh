#!/bin/bash
# Start the mitmproxy token tracker and set macOS system proxy

PROXY_PORT=8181
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PIDFILE="/tmp/pathless-mitm.pid"

if [ -f "$PIDFILE" ] && kill -0 "$(cat $PIDFILE)" 2>/dev/null; then
  echo "Proxy already running (PID $(cat $PIDFILE))"
  exit 0
fi

echo "Starting token tracker proxy on port $PROXY_PORT..."
mitmdump -s "$SCRIPT_DIR/mitm_addon.py" --listen-port $PROXY_PORT --quiet &
echo $! > "$PIDFILE"
sleep 1

echo "Setting macOS system HTTPS proxy..."
networksetup -setwebproxy Wi-Fi 127.0.0.1 $PROXY_PORT
networksetup -setsecurewebproxy Wi-Fi 127.0.0.1 $PROXY_PORT
networksetup -setwebproxystate Wi-Fi on
networksetup -setsecurewebproxystate Wi-Fi on

echo ""
echo "Token tracker running. PID: $(cat $PIDFILE)"
echo "All Anthropic API calls are now being tracked."
echo "Run ./proxy_stop.sh to stop."

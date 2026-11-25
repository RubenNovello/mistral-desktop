#!/usr/bin/env bash
export QTWEBENGINEPROCESS_PATH="/app/bin/QtWebEngineProcess"
exec python3 /app/share/mistral-desktop/main.py "$@"

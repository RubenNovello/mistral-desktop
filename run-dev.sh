#!/usr/bin/env bash
# Mistral Desktop — lancio da sorgente (dev)
cd "$HOME/mistral-desktop" || exit 1

# crea il venv solo se manca (la prima volta), poi usa il suo python
if [ ! -d .venv ]; then
    python3 -m venv .venv || exit 1
fi

exec .venv/bin/python main.py >> app.log 2>&1

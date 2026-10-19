#!/bin/sh
# Запуск GUI-эмулятора (вся логика на Python).
set -e

# Выбрать интерпретатор Python с рабочим Tk 8.6 (Tk 8.5 падает на новой macOS).
check_tk='import tkinter,sys; sys.exit(0 if tkinter.TkVersion>=8.6 else 1)'
PYTHON=""
for cand in python3 python3.14 python3.13 python3.12 python3.11; do
    if command -v "$cand" >/dev/null 2>&1 && "$cand" -c "$check_tk" >/dev/null 2>&1; then
        PYTHON="$cand"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo "No Python with Tk 8.6 found. Install python.org build or python-tk." >&2
    exit 1
fi

exec "$PYTHON" src/gui/main.py "$@"

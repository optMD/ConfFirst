#!/bin/sh
# Запуск только со стартовым скриптом (VFS не задан).
cd "$(dirname "$0")/.."
./run.sh --script scripts/startup_stage2.txt

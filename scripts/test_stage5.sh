#!/bin/sh
# Проверка команды этапа 5: mkdir и обработка ошибок.
cd "$(dirname "$0")/.."
./run.sh --vfs vfs/medium.csv --script scripts/startup_stage5.txt

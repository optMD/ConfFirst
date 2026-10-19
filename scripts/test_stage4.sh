#!/bin/sh
# Проверка команд этапа 4: ls, cd, uname, head, history и обработка ошибок.
cd "$(dirname "$0")/.."
./run.sh --vfs vfs/medium.csv --script scripts/startup_stage4.txt

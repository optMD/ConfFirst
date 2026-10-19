#!/bin/sh
# Проверка остановки стартового скрипта на первой ошибке.
cd "$(dirname "$0")/.."
./run.sh --vfs vfs/medium.csv --script scripts/startup_stage1.txt

#!/bin/sh
# Запуск со всеми параметрами: VFS и стартовый скрипт.
cd "$(dirname "$0")/.."
./run.sh --vfs vfs/medium.csv --script scripts/startup_stage2.txt

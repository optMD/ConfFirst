#!/bin/sh
# Запуск с минимальной VFS: корень и один файл.
cd "$(dirname "$0")/.."
./run.sh --vfs vfs/minimal.csv --script scripts/startup_stage3.txt

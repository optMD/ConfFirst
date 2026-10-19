#!/bin/sh
# Запуск с VFS из нескольких файлов и папок.
cd "$(dirname "$0")/.."
./run.sh --vfs vfs/medium.csv --script scripts/startup_stage3.txt

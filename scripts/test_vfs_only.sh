#!/bin/sh
# Запуск только с параметром VFS.
cd "$(dirname "$0")/.."
./run.sh --vfs vfs/medium.csv

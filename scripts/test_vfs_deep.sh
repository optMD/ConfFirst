#!/bin/sh
# Запуск с глубокой VFS: не менее трёх уровней вложенности.
cd "$(dirname "$0")/.."
./run.sh --vfs vfs/deep.csv --script scripts/startup_stage3.txt

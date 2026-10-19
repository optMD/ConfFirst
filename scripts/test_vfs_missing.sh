#!/bin/sh
# Ошибка загрузки: файл VFS не найден.
cd "$(dirname "$0")/.."
./run.sh --vfs vfs/no_such_file.csv

#!/bin/sh
# Ошибка загрузки: неверный формат CSV-файла.
cd "$(dirname "$0")/.."
./run.sh --vfs vfs/broken.csv

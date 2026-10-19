#!/bin/sh
# Проверка vfs-init: физический CSV-файл очищается.
cd "$(dirname "$0")/.."
tmp=$(mktemp)
cp vfs/medium.csv "$tmp"
./run.sh --vfs "$tmp" --script scripts/startup_vfs_init.txt
echo "size of $tmp: $(wc -c < "$tmp") bytes"
rm -f "$tmp"

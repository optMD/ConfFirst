"""Точка входа: разбор параметров и запуск GUI-эмулятора."""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.shell import Shell
from gui.terminal import Terminal


def parse_args() -> argparse.Namespace:
    """Разобрать параметры командной строки."""
    parser = argparse.ArgumentParser(description="VFS shell emulator")
    parser.add_argument("--vfs", default="", help="path to VFS CSV file")
    parser.add_argument("--script", default="", help="path to startup script")
    return parser.parse_args()


def vfs_name(path: str) -> str:
    """Получить имя VFS для заголовка окна."""
    if not path:
        return "default"
    return os.path.basename(path)


def main() -> None:
    """Запустить эмулятор."""
    args = parse_args()
    print(f"[debug] vfs path: {args.vfs or '(not set)'}")
    print(f"[debug] script path: {args.script or '(not set)'}")
    client = Shell(args.vfs)
    app = Terminal(vfs_name(args.vfs), client, args.script)
    try:
        app.mainloop()
    finally:
        client.close()


if __name__ == "__main__":
    main()

"""Командная оболочка над VFS: те же команды, что были в C-бэкенде.

Класс Shell заменяет пару «C-процесс + pipe-протокол»: он хранит
текущую папку, историю и VFS и возвращает готовый Response.
"""
from dataclasses import dataclass

from .parser import parse
from .vfs import Node, VFS, VfsError

STATUS_OK = 0
STATUS_ERROR = 1
HISTORY_MAX = 128
DEFAULT_HEAD_LINES = 10


@dataclass
class Response:
    """Результат команды: статус, текущая директория и тело вывода."""

    status: int
    cwd: str
    body: str


class Shell:
    """Долгоживущая сессия эмулятора: VFS, cwd и история команд."""

    def __init__(self, vfs_path: str = "") -> None:
        self._vfs_path = vfs_path
        self._history: list[str] = []
        if not vfs_path:
            self.vfs = VFS.default()
            self.startup = Response(STATUS_OK, "/", "vfs: default VFS loaded")
        else:
            try:
                self.vfs = VFS.load(vfs_path)
                self.startup = Response(STATUS_OK, "/", "vfs: loaded")
            except VfsError as error:
                self.vfs = VFS.default()
                self.startup = Response(STATUS_ERROR, "/", str(error))
        self._cwd = self.vfs.root

    def send(self, line: str) -> Response:
        """Выполнить одну строку ввода и вернуть ответ."""
        raw = line.rstrip("\n")
        if raw == "exit":
            return self._reply(STATUS_OK)
        if raw == "":
            return self._reply(STATUS_OK)

        self._history.append(raw)
        if len(self._history) > HISTORY_MAX:
            self._history.pop(0)

        if raw == "vfs-init":
            return self._vfs_init()

        parsed = parse(raw)
        if not parsed.name:
            return self._reply(STATUS_OK)
        handler = {
            "ls": self._ls,
            "cd": self._cd,
            "uname": self._uname,
            "head": self._head,
            "history": self._history_cmd,
            "mkdir": self._mkdir,
        }.get(parsed.name)
        if handler is None:
            return self._reply(STATUS_ERROR,
                               f"{parsed.name}: command not found")
        return handler(parsed.args)

    def close(self) -> None:
        """Совместимость с прежним клиентом бэкенда; ресурсов нет."""

    def _reply(self, status: int, body: str = "") -> Response:
        return Response(status, self._cwd.path(), body)

    def _resolve(self, arg: str) -> "Node | None":
        return self.vfs.resolve(self._cwd, arg)

    def _vfs_init(self) -> Response:
        self.vfs = VFS.default()
        self._cwd = self.vfs.root
        if self._vfs_path:
            try:
                with open(self._vfs_path, "w", encoding="utf-8"):
                    pass
            except OSError:
                return self._reply(
                    STATUS_ERROR, "vfs-init: cannot clear physical VFS")
        return self._reply(STATUS_OK, "vfs-init: reset to default VFS")

    def _ls(self, args: list[str]) -> Response:
        if len(args) > 1:
            return self._reply(STATUS_ERROR, "ls: too many arguments")
        node = self._cwd if not args else self._resolve(args[0])
        if node is None:
            return self._reply(STATUS_ERROR, "ls: no such file or directory")
        if not node.is_dir:
            return self._reply(STATUS_OK, node.name)
        return self._reply(STATUS_OK, "\n".join(node.children))

    def _cd(self, args: list[str]) -> Response:
        if len(args) > 1:
            return self._reply(STATUS_ERROR, "cd: too many arguments")
        node = self._resolve(args[0] if args else "/")
        if node is None:
            return self._reply(STATUS_ERROR, "cd: no such directory")
        if not node.is_dir:
            return self._reply(STATUS_ERROR, "cd: not a directory")
        self._cwd = node
        return self._reply(STATUS_OK)

    def _uname(self, args: list[str]) -> Response:
        if args:
            return self._reply(STATUS_ERROR, "uname: too many arguments")
        return self._reply(STATUS_OK, "Emulator")

    def _head(self, args: list[str]) -> Response:
        count = DEFAULT_HEAD_LINES
        file_index = 0
        if args and args[0] == "-n":
            if len(args) < 3:
                return self._reply(
                    STATUS_ERROR, "head: option -n needs a number")
            count = _atol(args[1])
            if count < 0:
                return self._reply(STATUS_ERROR,
                                   "head: invalid line count")
            file_index = 2
        if len(args) - file_index != 1:
            return self._reply(STATUS_ERROR, "head: need exactly one file")
        node = self._resolve(args[file_index])
        if node is None:
            return self._reply(STATUS_ERROR, "head: no such file")
        if node.is_dir:
            return self._reply(STATUS_ERROR, "head: not a file")
        text = node.content.decode("utf-8", errors="replace")
        lines = text.split("\n")
        if lines and lines[-1] == "":
            lines.pop()
        return self._reply(STATUS_OK, "\n".join(lines[:count]))

    def _history_cmd(self, args: list[str]) -> Response:
        if args:
            return self._reply(STATUS_ERROR, "history: too many arguments")
        return self._reply(STATUS_OK, "\n".join(self._history))

    def _mkdir(self, args: list[str]) -> Response:
        if len(args) != 1:
            return self._reply(STATUS_ERROR,
                               "mkdir: need exactly one path")
        try:
            self.vfs.mkdir(self._cwd, args[0])
        except VfsError as error:
            return self._reply(STATUS_ERROR, str(error))
        return self._reply(STATUS_OK)


def _atol(text: str) -> int:
    """Аналог C atol: ведущие цифры со знаком, иначе 0."""
    index = 0
    sign = 1
    if index < len(text) and text[index] in "+-":
        sign = -1 if text[index] == "-" else 1
        index += 1
    start = index
    while index < len(text) and text[index].isdigit():
        index += 1
    if start == index:
        return 0
    return sign * int(text[start:index])

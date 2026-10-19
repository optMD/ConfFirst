"""Виртуальная файловая система в виде дерева узлов.

Каждая папка и файл — объект Node со ссылкой на родителя и словарём
детей. Путь узла вычисляется подъёмом к корню, а поиск по пути —
спуском от корня.
"""
import base64
import binascii
from dataclasses import dataclass, field

CSV_FIELDS_MIN = 3
CSV_CONTENT_INDEX = 3
HEADER_ROW = 1


class VfsError(Exception):
    """Ошибка загрузки или изменения VFS."""


@dataclass(eq=False)
class Node:
    """Узел дерева: папка или файл.

    parent и children исключены из сравнения и repr, иначе взаимные
    ссылки родитель<->ребёнок дают бесконечную рекурсию.
    """

    name: str
    is_dir: bool
    owner: str = "root"
    content: bytes = b""
    parent: "Node | None" = field(default=None, repr=False, compare=False)
    children: "dict[str, Node]" = field(
        default_factory=dict, repr=False, compare=False)

    def path(self) -> str:
        """Полный путь узла, собранный подъёмом к корню."""
        if self.parent is None:
            return "/"
        parts = []
        node = self
        while node.parent is not None:
            parts.append(node.name)
            node = node.parent
        return "/" + "/".join(reversed(parts))


class VFS:
    """Дерево узлов с операциями загрузки, поиска и создания папок."""

    def __init__(self) -> None:
        self.root = Node(name="", is_dir=True)

    @classmethod
    def default(cls) -> "VFS":
        """VFS по умолчанию: только корневая папка."""
        return cls()

    @classmethod
    def load(cls, path: str) -> "VFS":
        """Загрузить VFS из CSV (тип,путь,владелец,содержимое-base64).

        Первая строка считается заголовком, пустые строки пропускаются.
        Записи упорядочиваются по глубине пути, чтобы родительские папки
        создавались раньше дочерних.
        """
        try:
            with open(path, encoding="utf-8") as handle:
                raw_lines = handle.read().splitlines()
        except OSError:
            raise VfsError(f"vfs: cannot open {path}")

        vfs = cls()
        entries = []
        for row, line in enumerate(raw_lines, start=HEADER_ROW):
            if row == HEADER_ROW or line == "":
                continue
            entries.append((row, _parse_line(row, line)))

        if not entries:
            raise VfsError(f"vfs: no entries in {path}")

        entries.sort(key=lambda item: item[1][1].count("/"))
        for _row, (is_dir, node_path, owner, content) in entries:
            vfs._place(node_path, is_dir, owner, content)
        return vfs

    def _place(self, node_path: str, is_dir: bool, owner: str,
               content: bytes) -> None:
        """Поместить узел по абсолютному пути, создавая папки по дороге.

        Пустой путь означает корень: обновляется его владелец.
        """
        parts = [p for p in node_path.split("/") if p]
        if not parts:
            self.root.owner = owner
            return
        node = self.root
        for part in parts[:-1]:
            child = node.children.get(part)
            if child is None:
                child = Node(name=part, is_dir=True, parent=node)
                node.children[part] = child
            node = child
        leaf_name = parts[-1]
        node.children[leaf_name] = Node(
            name=leaf_name, is_dir=is_dir, owner=owner,
            content=content, parent=node)

    def resolve(self, cwd: Node, arg: str) -> "Node | None":
        """Найти узел по пути arg относительно cwd (или от корня)."""
        parts = _normalize(cwd.path(), arg)
        node = self.root
        for part in parts:
            if not node.is_dir:
                return None
            node = node.children.get(part)
            if node is None:
                return None
        return node

    def mkdir(self, cwd: Node, arg: str) -> None:
        """Создать папку по пути arg; бросить VfsError при ошибке."""
        parts = _normalize(cwd.path(), arg)
        if not parts:
            raise VfsError("mkdir: already exists")
        node = self.root
        for part in parts[:-1]:
            node = node.children.get(part)
            if node is None or not node.is_dir:
                raise VfsError("mkdir: no such directory")
        name = parts[-1]
        if name in node.children:
            raise VfsError("mkdir: already exists")
        node.children[name] = Node(name=name, is_dir=True, parent=node)


def _parse_line(row: int, line: str):
    """Разобрать строку CSV в (is_dir, path, owner, content)."""
    fields = line.split(",")
    if len(fields) < CSV_FIELDS_MIN:
        raise VfsError(f"vfs: invalid format on line {row}")
    kind, node_path, owner = fields[0], fields[1], fields[2]
    data = fields[CSV_CONTENT_INDEX] if len(fields) > CSV_CONTENT_INDEX else ""
    if kind == "d":
        return (True, node_path, owner, b"")
    if kind == "f":
        try:
            padded = data + "=" * (-len(data) % 4)
            content = base64.b64decode(padded, validate=True) if data else b""
        except (ValueError, binascii.Error):
            raise VfsError(f"vfs: invalid format on line {row}")
        return (False, node_path, owner, content)
    raise VfsError(f"vfs: invalid format on line {row}")


def _normalize(cwd: str, arg: str) -> list[str]:
    """Свести путь к списку имён, обработав '.', '..' и абсолютность."""
    work = arg if arg.startswith("/") else f"{cwd}/{arg}"
    parts: list[str] = []
    for token in work.split("/"):
        if token in ("", "."):
            continue
        if token == "..":
            if parts:
                parts.pop()
        else:
            parts.append(token)
    return parts

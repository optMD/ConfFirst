"""Простой парсер ввода: разделение на команду и аргументы."""
from dataclasses import dataclass


@dataclass
class ParsedCommand:
    """Разобранная строка ввода."""

    name: str
    args: list[str]


def parse(line: str) -> ParsedCommand:
    """Разделить строку на команду и аргументы по пробелам."""
    parts = line.split()
    if not parts:
        return ParsedCommand("", [])
    return ParsedCommand(parts[0], parts[1:])

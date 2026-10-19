"""Тесты простого парсера команд."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from gui.parser import parse  # noqa: E402


class TestParse(unittest.TestCase):
    """Проверка разделения ввода на команду и аргументы."""

    def test_empty_line(self):
        """Пустая строка не содержит команды."""
        parsed = parse("   ")
        self.assertEqual(parsed.name, "")
        self.assertEqual(parsed.args, [])

    def test_command_with_args(self):
        """Команда и аргументы разделяются по пробелам."""
        parsed = parse("ls -l /home")
        self.assertEqual(parsed.name, "ls")
        self.assertEqual(parsed.args, ["-l", "/home"])

    def test_command_without_args(self):
        """Команда без аргументов."""
        parsed = parse("exit")
        self.assertEqual(parsed.name, "exit")
        self.assertEqual(parsed.args, [])


if __name__ == "__main__":
    unittest.main()

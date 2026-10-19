"""Графическое окно эмулятора на tkinter."""
import tkinter as tk

from .parser import parse
from .shell import Shell

BUILTIN_COMMANDS = ("ls", "cd", "uname", "head", "history", "mkdir",
                    "vfs-init")
EXIT_COMMAND = "exit"
STATUS_OK = "ok"
STATUS_ERROR = "error"
STATUS_EXIT = "exit"


class Terminal(tk.Tk):
    """Главное окно: поле вывода, строка ввода, связь с оболочкой."""

    def __init__(self, vfs_name: str, client: Shell,
                 script: str = "") -> None:
        super().__init__()
        self.title(f"Emulator - {vfs_name}")
        self._client = client
        self._cwd = "/"
        self._output = tk.Text(self, state="disabled")
        self._output.pack(fill="both", expand=True)
        self._entry = tk.Entry(self)
        self._entry.pack(fill="x")
        self._entry.bind("<Return>", self._on_enter)
        self._entry.focus_set()
        self.lift()
        self.attributes("-topmost", True)
        self.after_idle(self._release_topmost)
        self.after_idle(self._entry.focus_force)
        if script:
            self.after(0, lambda: self.run_script(script))
        if client.startup.body:
            self.print_line(client.startup.body)

    def _release_topmost(self) -> None:
        self.attributes("-topmost", False)

    def print_line(self, text: str) -> None:
        """Добавить строку в поле вывода."""
        self._output.configure(state="normal")
        self._output.insert("end", text + "\n")
        self._output.configure(state="disabled")
        self._output.see("end")

    def prompt(self) -> str:
        """Сформировать приглашение к вводу с именем VFS."""
        return f"VFS:{self._cwd}$"

    def _on_enter(self, _event: object) -> None:
        raw = self._entry.get()
        self._entry.delete(0, "end")
        self.run_line(raw)

    def run_script(self, path: str) -> None:
        """Выполнить стартовый скрипт, остановиться на первой ошибке."""
        try:
            with open(path, encoding="utf-8") as handle:
                lines = handle.read().splitlines()
        except OSError as error:
            self.print_line(f"script: {error}")
            return
        for raw in lines:
            status = self.run_line(raw)
            if status == STATUS_EXIT:
                return
            if status == STATUS_ERROR:
                self.print_line("script: stopped on error")
                return

    def run_line(self, raw: str) -> str:
        """Выполнить одну строку ввода, вернуть статус выполнения."""
        self.print_line(f"{self.prompt()} {raw}")
        parsed = parse(raw)
        if not parsed.name:
            return STATUS_OK
        if parsed.name == EXIT_COMMAND:
            self._client.send(EXIT_COMMAND)
            self.destroy()
            return STATUS_EXIT
        if parsed.name not in BUILTIN_COMMANDS:
            self.print_line(f"{parsed.name}: command not found")
            return STATUS_ERROR
        response = self._client.send(raw)
        if response.body:
            self.print_line(response.body)
        self._cwd = response.cwd
        if response.status != 0:
            return STATUS_ERROR
        return STATUS_OK

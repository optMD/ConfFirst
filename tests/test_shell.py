"""Тесты оболочки и загрузки VFS."""
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from gui.shell import Shell  # noqa: E402

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
MEDIUM = os.path.join(REPO_ROOT, "vfs", "medium.csv")


def run(commands, vfs=None):
    """Выполнить команды в оболочке, вернуть стартовый ответ и ответы."""
    shell = Shell(vfs or "")
    frames = [shell.startup]
    for command in commands:
        if command == "exit":
            break
        frames.append(shell.send(command))
    return frames


class TestMainCommands(unittest.TestCase):
    """Проверка команд ls, cd, uname, head, history, mkdir."""

    def test_ls_current_and_path(self):
        result = run(["ls", "ls /home", "exit"], MEDIUM)
        self.assertEqual(result[1].body, "home\netc")
        self.assertEqual(result[2].body, "readme.txt\nnotes.txt")

    def test_ls_errors(self):
        result = run(["ls /nope", "ls a b", "exit"], MEDIUM)
        self.assertEqual(result[1].status, 1)
        self.assertEqual(result[2].status, 1)

    def test_cd_changes_cwd(self):
        result = run(["cd /home", "cd ..", "exit"], MEDIUM)
        self.assertEqual(result[1].cwd, "/home")
        self.assertEqual(result[2].cwd, "/")

    def test_cd_errors(self):
        result = run(["cd /nope", "cd /home/readme.txt", "exit"], MEDIUM)
        self.assertEqual(result[1].status, 1)
        self.assertEqual(result[2].status, 1)
        self.assertEqual(result[2].cwd, "/")

    def test_uname(self):
        result = run(["uname", "exit"], MEDIUM)
        self.assertEqual(result[1].status, 0)
        self.assertEqual(result[1].body, "Emulator")

    def test_head(self):
        result = run(["head /etc/motd", "head -n 2 /home/notes.txt",
                      "exit"], MEDIUM)
        self.assertEqual(result[1].body, "System ready")
        self.assertEqual(result[2].body, "line1\nline2")

    def test_head_errors(self):
        result = run(["head", "head /etc", "head /nope", "exit"], MEDIUM)
        for frame in result[1:4]:
            self.assertEqual(frame.status, 1)

    def test_history(self):
        result = run(["uname", "history", "exit"], MEDIUM)
        self.assertEqual(result[2].body, "uname\nhistory")

    def test_mkdir(self):
        result = run(["mkdir /home/new", "ls /home", "exit"], MEDIUM)
        self.assertEqual(result[1].status, 0)
        self.assertIn("new", result[2].body.splitlines())

    def test_mkdir_errors(self):
        result = run(["mkdir /home", "mkdir /nope/x", "mkdir", "exit"], MEDIUM)
        for frame in result[1:4]:
            self.assertEqual(frame.status, 1)


class TestVfsLoading(unittest.TestCase):
    """Проверка загрузки VFS из CSV и команды vfs-init."""

    def test_default_vfs(self):
        startup = run(["exit"])[0]
        self.assertEqual(startup.status, 0)
        self.assertIn("default", startup.body)

    def test_load_medium(self):
        startup = run(["exit"], MEDIUM)[0]
        self.assertEqual(startup.status, 0)

    def test_missing_file(self):
        startup = run(["exit"], "/no/such/vfs.csv")[0]
        self.assertEqual(startup.status, 1)
        self.assertIn("cannot open", startup.body)

    def test_invalid_format(self):
        handle, path = tempfile.mkstemp(suffix=".csv")
        with os.fdopen(handle, "w", encoding="utf-8") as file:
            file.write("type,path,owner,content\nx,/bad,root,\n")
        try:
            startup = run(["exit"], path)[0]
        finally:
            os.unlink(path)
        self.assertEqual(startup.status, 1)
        self.assertIn("invalid format", startup.body)

    def test_vfs_init_clears_file(self):
        handle, path = tempfile.mkstemp(suffix=".csv")
        os.close(handle)
        shutil.copyfile(MEDIUM, path)
        try:
            result = run(["vfs-init", "exit"], path)
            self.assertEqual(result[1].status, 0)
            self.assertEqual(os.path.getsize(path), 0)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()

# tests/test_log_cli.py
import sys
import types
import pytest

from src.task3 import main

def test_cli_counts_only(monkeypatch, capsys, tmp_path):
    content = (
        "2024-01-22 08:30:01 INFO A\n"
        "2024-01-22 08:45:23 DEBUG B\n"
        "2024-01-22 09:00:45 ERROR C\n"
    )
    p = tmp_path / "x.log"
    p.write_text(content, encoding="utf-8")

    monkeypatch.setattr(sys, "argv", ["prog", str(p)])
    main()
    out = capsys.readouterr().out
    assert "INFO" in out and "DEBUG" in out and "ERROR" in out

def test_cli_with_level(monkeypatch, capsys, tmp_path):
    content = (
        "2024-01-22 08:30:01 INFO A\n"
        "2024-01-22 09:00:45 ERROR C\n"
    )
    p = tmp_path / "y.log"
    p.write_text(content, encoding="utf-8")

    monkeypatch.setattr(sys, "argv", ["prog", str(p), "error"])
    main()
    out = capsys.readouterr().out
    assert "Деталі логів" in out
    assert "ERROR" in out and "C" in out

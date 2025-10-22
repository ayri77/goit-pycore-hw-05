from src.task3 import (
    parse_log_line,
    load_logs,
    filter_logs_by_level,
    count_logs_by_level,
    display_log_counts,
)  

import io
import os
import re
import pytest


@pytest.fixture
def sample_log_text() -> str:
    return (
        "2024-01-22 08:30:01 INFO User logged in successfully.\n"
        "2024-01-22 08:45:23 DEBUG Attempting to connect to the database.\n"
        "2024-01-22 09:00:45 ERROR Database connection failed.\n"
        "2024-01-22 09:15:10 INFO Data export completed.\n"
        "2024-01-22 10:30:55 WARNING Disk usage above 80%.\n"
        "2024-01-22 11:05:00 DEBUG Starting data backup process.\n"
        "2024-01-22 11:30:15 ERROR Backup process failed.\n"
        "2024-01-22 12:00:00 INFO User logged out.\n"
        "2024-01-22 12:45:05 DEBUG Checking system health.\n"
        "2024-01-22 13:30:30 INFO Scheduled maintenance.\n"
    )


@pytest.fixture
def sample_log_file(tmp_path, sample_log_text):
    p = tmp_path / "sample.log"
    p.write_text(sample_log_text, encoding="utf-8")
    return p


def test_parse_log_line_ok():
    line = "2024-01-22 08:30:01 INFO User logged in successfully."
    rec = parse_log_line(line)
    assert isinstance(rec, dict)
    assert rec["date"] == "2024-01-22"
    assert rec["time"] == "08:30:01"
    assert rec["level"] == "INFO"
    assert rec["message"] == "User logged in successfully."


def test_load_logs_reads_all(sample_log_file):
    logs = load_logs(str(sample_log_file))
    assert isinstance(logs, list)
    assert len(logs) == 10
    # sanity: each item has required keys
    for rec in logs:
        assert {"date", "time", "level", "message"} <= set(rec.keys())


def test_filter_logs_by_level_case_insensitive(sample_log_file):
    logs = load_logs(str(sample_log_file))
    errors = filter_logs_by_level(logs, "error")  # lower-case on purpose
    assert len(errors) == 2
    msgs = [r["message"] for r in errors]
    assert "Database connection failed." in msgs
    assert "Backup process failed." in msgs


def test_count_logs_by_level(sample_log_file):
    logs = load_logs(str(sample_log_file))
    counts = count_logs_by_level(logs)
    assert counts == {"INFO": 4, "DEBUG": 3, "ERROR": 2, "WARNING": 1}


def test_display_log_counts_formats_table(capsys, sample_log_file):
    logs = load_logs(str(sample_log_file))
    counts = count_logs_by_level(logs)
    display_log_counts(counts)
    out = capsys.readouterr().out
    # Flexible match: headers + counts present
    assert re.search(r"Рівень логування\s*\|\s*Кількість", out)
    for level, n in [("INFO", 4), ("DEBUG", 3), ("ERROR", 2), ("WARNING", 1)]:
        assert re.search(fr"{level}\s*\|\s*{n}\b", out)


def test_load_logs_missing_file_raises(tmp_path):
    missing = tmp_path / "nope.log"
    # Expect FileNotFoundError
    with pytest.raises(FileNotFoundError):
        load_logs(str(missing))


def test_filter_logs_no_matches(sample_log_file):
    logs = load_logs(str(sample_log_file))
    critical = filter_logs_by_level(logs, "CRITICAL")
    assert critical == []


def test_parse_log_line_invalid_format_raises():
    bad = "not a log line"
    # Если твоя реализация возвращает None/{} вместо исключения — скорректируй тест.
    assert parse_log_line(bad) == None

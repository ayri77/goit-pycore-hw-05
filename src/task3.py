# -----------------------------------------------------------------------
# -------------------------TASK DESCRIPTION------------------------------
# -----------------------------------------------------------------------
'''
Розробіть Python-скрипт для аналізу файлів логів. Скрипт повинен вміти читати лог-файл, 
переданий як аргумент командного рядка, і виводити статистику за рівнями логування наприклад, 
INFO, ERROR, DEBUG. Також користувач може вказати рівень логування як другий аргумент 
командного рядка, щоб отримати всі записи цього рівня.

Файли логів – це файли, що містять записи про події, які відбулися в операційній системі, 
програмному забезпеченні або інших системах. Вони допомагають відстежувати та аналізувати 
поведінку системи, виявляти та діагностувати проблеми.

Скрипт виконує всі зазначені вимоги, правильно аналізуючи лог-файли та виводячи інформацію.
Скрипт коректно обробляє помилки, такі як неправильний формат лог-файлу або відсутність файлу.
При розробці обов'язково було використано один з елементів функціонального програмування: лямбда-функція, списковий вираз, функція filter, тощо.
Код добре структурований, зрозумілий і містить коментарі там, де це необхідно.
'''


# -----------------------------------------------------------------------
# -------------------------TASK SOLUTION---------------------------------
# -----------------------------------------------------------------------

'''
Функції:
1. CLI інтерфейс: приймає шлях до файла, та опційно рівень деталізації логів
2. Генератор, який буде отримувати построчно лог
3. Функція парсінгу строки лога
4. Функція обробки лога за типом запису: формування детального лога, якщо необхідно
5. Функція підрахунку кількості за типом
6. Вивід логів

'''
import sys
import os
from pathlib import Path
from collections import Counter
import re

LOG_LEVELS = (
    "INFO",
    "DEBUG",
    "ERROR",
    "WARNING"
)

# sample 2024-01-22 13:30:30 INFO Scheduled maintenance.
levels_re = "|".join(map(re.escape, LOG_LEVELS))
pattern = re.compile(
    rf'^(?P<date>\d{{4}}-\d{{2}}-\d{{2}})\s+'
    rf'(?P<time>\d{{2}}:\d{{2}}:\d{{2}})\s+'
    rf'(?P<level>{levels_re})\s+'
    rf'(?P<message>.+)$'
)
# parsing one log line
def parse_log_line(line: str) -> dict|None:
    '''
    Parsing log line into dict = {LEVEL, DATE, TIME, MESSAGE}
    '''

    m = pattern.fullmatch(line.strip())
    if not m:
        return None # return None, when not match pattern
    d = m.groupdict()
    return d

# load log file
def load_logs(path: str | os.PathLike[str]) -> list:
    '''
    Loading log-file and parsing in list with dict
    '''
    with open(path, mode="r", encoding="utf-8") as f:
        return [rec for l in f if (rec := parse_log_line(l)) is not None] # check for None
    

def filter_logs_by_level(logs: list, level: str) -> list:
    '''
    Filtering log list with provided loglevel. Return filtered log
    '''
    lvl = level.upper()
    return [rec for rec in logs if rec.get("level", "").upper() == lvl]

def count_logs_by_level(logs: list) -> dict:
    '''
    Count level logs, 0 if no records for log level
    '''
    c = Counter(rec.get("level") for rec in logs)
    return {lvl: c.get(lvl, 0) for lvl in LOG_LEVELS}

def display_log_counts(counts: dict):
    '''
    Print statistic
    '''
    print("Рівень логування | Кількість")
    print("-----------------|----------")

    for level, count in counts.items():
        print(f"{level:<17}| {count:>8}")

def display_level_details(level: str, rows: list[dict]):
    '''
    Print details
    '''
    print(f"\nДеталі логів для рівня '{level.upper()}':")
    for r in rows:
        print(f"{r['date']} {r['time']} - {r['message']}")

# -----------------------------------------------------------------------
def main():

    args = sys.argv
    # ------------- 
    # check args
    if len(args) == 1:
        print("usage: python main.py <logfile> [level]", file=sys.stderr)
        sys.exit(2)
    if len(args) > 3:
        print("error: too many arguments", file=sys.stderr)
        sys.exit(2)

    path = Path(args[1])
    if not path.exists():
        print("error: file not found", file=sys.stderr)
        sys.exit(1)
    if not path.is_file():
        print("error: path is a directory", file=sys.stderr)
        sys.exit(1)

    level_filter = args[2] if len(args) == 3 else ""
    if level_filter and level_filter.upper() not in LOG_LEVELS:
        print(f"error: accepting log-levels {LOG_LEVELS}", file=sys.stderr)
        sys.exit(3)
    # ------------- 
    

    logs = load_logs(path)
    counts = count_logs_by_level(logs)
    display_log_counts(counts)
    
    if level_filter:
        filtered_logs = filter_logs_by_level(logs, level_filter)
        display_level_details(level_filter, filtered_logs)    


if __name__ == "__main__":
    main()
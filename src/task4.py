# -----------------------------------------------------------------------
# -------------------------TASK DESCRIPTION------------------------------
# -----------------------------------------------------------------------
'''
Доробіть консольного бота помічника з попереднього домашнього завдання та додайте обробку помилок за допомоги декораторів.

Вимоги до завдання:

Всі помилки введення користувача повинні оброблятися за допомогою декоратора input_error. Цей декоратор відповідає за 
повернення користувачеві повідомлень типу "Enter user name", "Give me name and phone please" тощо.
Декоратор input_error повинен обробляти винятки, що виникають у функціях - handler і це винятки: 
KeyError, ValueError, IndexError. Коли відбувається виняток декоратор повинен повертати відповідну відповідь користувачеві. 
Виконання програми при цьому не припиняється.
'''
# -----------------------------------------------------------------------
# -------------------------TASK SOLUTION---------------------------------
# -----------------------------------------------------------------------

'''
Додати блок декораторів та переписати контроль введення даних
на використання декораторів
'''

import sys
from pathlib import Path

import colorama
from colorama import Fore, Style

import re
import json

import shlex # support names with spaces

from typing import Callable
from functools import wraps # support decorators

# -----------------------------------------------------------------------
# ---------------------------Constants-----------------------------------
# -----------------------------------------------------------------------

# it will be better to use external ini files :)

# Basic message
MSG_WELCOME = "Welcome to the assistant bot!"
MSG_HELLO = "How can I help you?"
MSG_ADDED = "Contact added."
MSG_DUPLICATED = "Contact already exist."
MSG_UPDATED = "Contact updated."
MSG_DELETED = "Contact deleted."
MSG_DELETED_ALL = "All contacts deleted."
MSG_NOT_FOUND = "Contact not found."
MSG_ENTER_NAME_PHONE = "Enter user name and phone"
MSG_INVALID = "Invalid command."
MSG_GOODBYE = "Good bye!"
MSG_CONFIRM = "Type YES to confirm: "
MSG_CANCEL = "Canceled."

COMMAND_YES = "YES"
# Commands with aliases
COMMANDS_HELLO = ["hello", "hi"]
COMMANDS_HELP = ["help"]
COMMANDS_ADD = ["add"]
COMMANDS_CHANGE = ["change"]
COMMANDS_DELETE = ["delete"] # "delete all" version
COMMANDS_PHONE = ["phone"]
COMMANDS_ALL = ["all"]
COMMANDS_EXIT = ["close", "exit"]

# Short help (with marks)
MSG_HELP_SHORT = (
    "Assistant bot — команди:\n"
    "[cmd]hello[/cmd] | [cmd]hi[/cmd] — \"How can I help you?\"\n"
    "[cmd]help[/cmd] — показати довідку\n"
    "[cmd]add[/cmd] [arg]<ім’я>[/arg] [arg]<телефон>[/arg] — додати/перезаписати контакт\n"
    "[cmd]change[/cmd] [arg]<ім’я>[/arg] [arg]<новий_телефон>[/arg] — змінити номер\n"
    "[cmd]phone[/cmd] [arg]<ім’я>[/arg] — показати номер\n"
    "[cmd]delete[/cmd] [arg]<ім’я>[/arg] — видалити контакт\n"
    "[cmd]delete all[/cmd] — очистити всі контакти (підтвердіть [em]YES[/em])\n"
    "[cmd]all[/cmd] — показати всі контакти у форматі \"Name: phone\"\n"
    "[cmd]close[/cmd] | [cmd]exit[/cmd] — завершити роботу (\"Good bye!\")\n"
    "Правила: команди без урахування регістру; імена у Title Case; дані пишуться в .contacts.json при виході."
)

# Full help (with marks)
MSG_HELP = (
    "Assistant bot — довідка\n"
    "\n"
    "Основні команди:\n"
    "  [cmd]hello[/cmd] | [cmd]hi[/cmd]\n"
    "    Відповідь: \"How can I help you?\"\n"
    "\n"
    "  [cmd]help[/cmd]\n"
    "    Показати це повідомлення.\n"
    "\n"
    "  [cmd]add[/cmd] [arg]<ім’я>[/arg] [arg]<телефон>[/arg]\n"
    "    Додати або перезаписати контакт.\n"
    "    Приклад: [cmd]add[/cmd] [arg]John[/arg] [arg]123456789[/arg]\n"
    "\n"
    "  [cmd]change[/cmd] [arg]<ім’я>[/arg] [arg]<новий_телефон>[/arg]\n"
    "    Змінити номер існуючого контакту.\n"
    "    Приклад: [cmd]change[/cmd] [arg]John[/arg] [arg]0987654321[/arg]\n"
    "\n"
    "  [cmd]phone[/cmd] [arg]<ім’я>[/arg]\n"
    "    Показати номер телефону контакту.\n"
    "    Приклад: [cmd]phone[/cmd] [arg]John[/arg]\n"
    "\n"
    "  [cmd]delete[/cmd] [arg]<ім’я>[/arg]\n"
    "    Видалити контакт.\n"
    "    Приклад: [cmd]delete[/cmd] [arg]John[/arg]\n"
    "\n"
    "  [cmd]delete all[/cmd]\n"
    "    Очистити всі контакти (потрібне підтвердження: введіть [em]YES[/em]).\n"
    "\n"
    "  [cmd]all[/cmd]\n"
    "    Показати всі контакти у форматі \"Name: phone\".\n"
    "    Якщо контактів немає — \"No contacts.\".\n"
    "\n"
    "  [cmd]close[/cmd] | [cmd]exit[/cmd]\n"
    "    Завершити роботу бота. Відповідь: \"Good bye!\".\n"
    "\n"
    "Правила:\n"
    "• Команди нечутливі до регістру.\n"
    "• Імена зберігаються у Title Case (напр.: \"john doe\" → \"John Doe\").\n"
    "• Імена з пробілами пишіть у лапках: add \"Mary Jane\" 12345"
    "• Дані зберігаються у файлі .contacts.json під час виходу."
    "• Не виконується контроль дублікатів."
)

# path to storage
STORAGE = ".contacts.json"

# 
ERROR_MSG = {
    KeyError:  MSG_NOT_FOUND,
    IndexError: MSG_ENTER_NAME_PHONE,
    ValueError: MSG_INVALID,
}

# -----------------------------------------------------------------------
# ---------------------------Decorators-------------------------------------
# -----------------------------------------------------------------------

# input errors handling
def input_error(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (KeyError, IndexError) as e:
            # для этих типов игнорируем str(e)
            return ERROR_MSG[type(e)]
        except ValueError as e:
            msg = str(e).strip()
            return msg if msg else ERROR_MSG[ValueError]
    return wrapper

# -----------------------------------------------------------------------
# ---------------------------Utility-------------------------------------
# -----------------------------------------------------------------------

# load json
def load_contacts(path: str) -> dict[str, str]:
    '''
    load contacts from json file
    Args:
        path: path to json file
    Return:
        dict with contacts
    '''
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# save json
def save_contacts(path: str, contacts: dict[str, str]) -> None:
    '''
    save contacts to json file
    Args:
        path: path to json file
        contacts: dict with contacts
    Return:
        None
    '''
    with open(path, "w+", encoding="utf-8") as f:
        json.dump(contacts, f, ensure_ascii=False, indent=2)

# name normalization
def norm_name(name: str) -> str:
    '''
    normalize name to Title Case
    Args:
        name: raw name string
    Return:
        normalized name string
    '''
    return name.strip().title()

# -------------------- colorama formatting ------------------------------
TAGS = {
    "cmd": Fore.CYAN + Style.BRIGHT,
    "arg": Fore.MAGENTA,
    "em":  Style.BRIGHT,
    "name": Fore.LIGHTGREEN_EX,
    "phone": Fore.LIGHTMAGENTA_EX,
}
TAG_RE = re.compile(r"\[(cmd|arg|em|name|phone)\](.*?)\[/\1\]")

PALETTE = {
    "ok":   Fore.GREEN,
    "err":  Fore.RED,
    "info": Fore.CYAN,
    "warn": Fore.YELLOW,
}


def colorize_markers(text: str, kind: str | None = None) -> str:
    '''
    Colorize text markers [cmd], [arg], [em], [name], [phone]
    Args:
        text: input text with markers
        kind: optional kind for full text coloring
        Return:
        colored text
    '''
    def repl(m):
        tag, inner = m.group(1), m.group(2)
        return f"{TAGS[tag]}{inner}{Style.RESET_ALL}"
    colored = TAG_RE.sub(repl, text)

    if kind and kind in PALETTE:
        return f"{PALETTE[kind]}{colored}{Style.RESET_ALL}"
    return colored

# -----------------------------------------------------------------------
# ---------------------------Handlers------------------------------------
# -----------------------------------------------------------------------

# re phone number test
ALLOWED_PATTERN = re.compile(r'^\+?[\d\s\-\./()]+$')
def normalize_phone(raw: str) -> str:
    '''
    normalize phone number
    Args:
        raw: raw phone number string
    Return:
        normalized phone number string
    Raise:
        ValueError: if phone is invalid        
    '''
    s = raw.strip()
    if not s:
        raise ValueError("Phone is empty")
    if not ALLOWED_PATTERN.fullmatch(s):
        raise ValueError("Phone contains invalid chars")
    if s.count('+') > 1 or ('+' in s and not s.startswith('+')):
        raise ValueError("Plus sign must be at start and only once")
    digits = re.sub(r'\D', '', s)
    if not (7 <= len(digits) <= 15):
        raise ValueError("Phone must have 7..15 digits")
    return ('+' if s.startswith('+') else '') + digits

# add contact in datbase
@input_error
def add_contact(args: list[str], contacts: dict[str, str]) -> str:
    '''
    adding contact to contacts dict
    Args:
        args: list with name and phone
        contacts: dict with contacts
    Return:
        message string
    '''
    if len(args) < 2:
        raise IndexError
    name, phone = norm_name(args[0]), args[1].strip()
    phone = normalize_phone(phone)
    contacts[name] = phone
    return MSG_ADDED

# change contact phone
@input_error
def change_contact(args: list[str], contacts: dict[str, str]) -> str:
    '''
    changing contact phone in contacts dict
    Args:
        args: list with name and new phone
        contacts: dict with contacts
    Return:
        message string
    '''
    if len(args) < 2:
        raise IndexError
    name, phone = norm_name(args[0]), args[1].strip()
    phone = normalize_phone(phone)
    if name in contacts:
        contacts[name] = phone
        return MSG_UPDATED
    else:
        raise KeyError(MSG_NOT_FOUND)

# delete contact
@input_error
def delete_contact(args: list[str], contacts: dict[str, str]) -> str:
    '''
    deleting contact from contacts dict
    Args:
        args: list with name
        contacts: dict with contacts
    Return:
        message string        
    '''
    if len(args) != 1:
        raise IndexError
    name = norm_name(args[0])
    if name in contacts:
        contacts.pop(name)
        return MSG_DELETED
    else:
        raise KeyError(MSG_NOT_FOUND)

@input_error
def delete_all(contacts: dict[str, str]) -> str:
    '''
    deleting all contacts from contacts dict
    Args:
        contacts: dict with contacts
        Return:
        message string
    '''
    if len(contacts) == 0:
        raise KeyError(MSG_NOT_FOUND)
    else:
        contacts.clear()
        return MSG_DELETED_ALL

@input_error
def show_phone(args: list[str], contacts: dict[str, str]) -> str:
    '''
    showing contact phone from contacts dict
    Args:
        args: list with name
        contacts: dict with contacts
    Return:
        message string
    '''
    if len(args) != 1:
        raise IndexError
    name = norm_name(args[0])    
    if name in contacts:
        phone = contacts.get(name)
        return f"[name]{name.strip()}[/name]: [phone]{phone.strip()}[/phone]"
    else:
        raise KeyError(MSG_NOT_FOUND)

def show_all(contacts: dict[str, str]) -> str:
    if not contacts:
        return "No contacts."
    
    lines =     ["--------------------------|--------------------"]
    lines.append("          Contact         |     Phone Number   ")
    lines.append("--------------------------|--------------------")
    for name in sorted(contacts):
        phone = contacts[name]
        lines.append(f"[name]{name:<26}[/name] [phone]{phone:>20}[/phone]")
    return "\n".join(lines)


# -----------------------------------------------------------------------
# ---------------------------Interface-----------------------------------
# -----------------------------------------------------------------------

# parsing message from user
# return command and arguments
def parse_input(user_input: str) -> tuple[str, list[str]]:
    '''
    Args:
        user input string
    Return     
        command 
        args list
    '''
    user_input = user_input.strip()
    if user_input == "":
        raise ValueError(MSG_INVALID)    
    
    try:
        cmd, *args = shlex.split(user_input)
    except ValueError:
        raise ValueError(MSG_INVALID)
    
    cmd = cmd.strip().lower()

    if args == []:
        # commands without args
        if cmd in COMMANDS_HELLO:
            return ("hello", [])
        elif cmd in COMMANDS_HELP:
            return ("help", [])
        elif cmd in COMMANDS_EXIT:
            return ("exit", [])
        elif cmd in COMMANDS_ALL:
            return ("show_all",[])
        else:
            raise ValueError(MSG_INVALID)
    else:
        # commands with args
        args_count  = len(args)
        if cmd in COMMANDS_ADD:
            return ("add", args)
        elif cmd in COMMANDS_CHANGE:
            return ("change", args)
        elif cmd in COMMANDS_DELETE and args_count == 1 and args[0].strip() == "all":            
            return ("delete_all", [])
        elif cmd in COMMANDS_DELETE and args_count == 1:
            return ("delete", [args[0].strip()])
        elif cmd in COMMANDS_PHONE:
            return ("phone", [args[0].strip()])
        else:
            raise ValueError(MSG_INVALID)

# processing command
def process_line(command, args, contacts) -> tuple[str, bool]:
    '''
    Args:
        command
        arguments
    Return:
        answer message
        boolean exit flag
    '''
    if command == "hello":
        return (MSG_HELLO, False)
    elif command == "help":
        return (MSG_HELP, False)
    elif command == "exit":
        return (MSG_GOODBYE, True)
    elif command == "phone":
        return (show_phone(args, contacts), False)
    elif command == "add":
        return (add_contact(args, contacts), False)
    elif command == "change":
        return (change_contact(args, contacts), False)
    elif command == "delete":
        return (delete_contact(args, contacts), False)
    elif command == "delete_all":
        return (delete_all(contacts), False)
    elif command == "show_all":
        return (show_all(contacts), False)
    elif command == "error":
        raise ValueError(MSG_INVALID)
    else:
        raise ValueError(MSG_INVALID)

# -----------------------------------------------------------------------
# -----------------------------main--------------------------------------
# -----------------------------------------------------------------------

def main():
    
    colorama.init(autoreset=True)

    # loading contacts
    # if file not exist. create JSON
    if not Path(STORAGE).exists():
        contacts_data = {}
    else:
        with open(STORAGE) as json_file:
            try:
                contacts_data = load_contacts(STORAGE)
            except:
                contacts_data = {}

    # Welcome message
    print(colorize_markers(MSG_WELCOME, "info"))
    print(colorize_markers(MSG_HELP_SHORT, "info"))
        
    while True:
        # while not exit command cycle
        input_data = input("Enter a command: ")
        command, args = parse_input(input_data)

        if command == "delete_all":
            input_data = input((colorize_markers(MSG_CONFIRM, "warn")))
            if input_data.upper() != COMMAND_YES:
                print(colorize_markers(MSG_CANCEL,"warn"))
                continue

        answer, exit_flag = process_line(command, args, contacts_data)
        
        if answer in (MSG_ADDED, MSG_UPDATED, MSG_DELETED, MSG_DELETED_ALL, MSG_GOODBYE):
            kind = "ok"
        elif answer in (MSG_INVALID, MSG_NOT_FOUND, MSG_DUPLICATED) or answer.lower().startswith("usage:"):
            kind = "err"
        elif answer in (MSG_HELP, MSG_HELP_SHORT, MSG_HELLO, MSG_WELCOME):
            kind = "info"
        elif "no contacts" in answer.lower():
            kind = "warn"
        else:
            kind = None       

        # formatting answer and print
        print(colorize_markers(answer, kind))

        # if exit command 
        if exit_flag:
            save_contacts(STORAGE, contacts_data)
            sys.exit(0)            

if __name__ == "__main__":
    main()
    
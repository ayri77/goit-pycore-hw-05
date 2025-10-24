import pytest
from src.task4 import add_contact, change_contact, delete_contact, show_phone, delete_all, normalize_phone, parse_input, process_line  
from src.task4 import MSG_ADDED, MSG_ENTER_NAME_PHONE, MSG_UPDATED, MSG_NOT_FOUND, MSG_DELETED, MSG_DELETED_ALL, MSG_HELLO, MSG_GOODBYE, MSG_HELP

# -------------------- Tests for task4.py functions ----------------------

@pytest.mark.parametrize(
    "raw, expected",
    [
        ("+49 176 12345678", "+4917612345678"),
        ("(093) 123-45-67",  "0931234567"),
        ("380-44/123.45.67", "380441234567"),
        ("012 345 67",       "01234567"),
        ("+1 (202) 555-01-01", "+12025550101"),
        ("  +44 20 7946 0958  ", "+442079460958"),
        ("1234567",          "1234567"),
    ],
    ids=["intl_plus","ua_parens","mix_sep","short_local","us_fmt","spaces_trim","min_len"]
)
def test_normalize_phone_ok(raw, expected):
    assert normalize_phone(raw) == expected

@pytest.mark.parametrize(
    "raw",
    [
        "++49 176 123",      
        "49+176123",         
        "123-abc-456",       
        "+1",                
        "",                  
        "   ",               
        "+1234567890123456", 
    ],
    ids=["double_plus","plus_inside","letters","too_short","+empty","spaces_only","too_long"]
)
def test_normalize_phone_errors(raw):
    with pytest.raises(ValueError):
        normalize_phone(raw)

# -------------------- add_contact tests ------------------------------
@pytest.mark.parametrize(
    "args, expected_contacts",
    [
        (["John", "+49 176 12345678"], {"John": "+4917612345678"}),
        (["John Doe", "(093) 123-45-67"], {"John Doe": "0931234567"}),
    ],
    ids=["intl","quoted_name_local"]
)
def test_add_contact_ok(args, expected_contacts):
    contacts = {}
    msg = add_contact(args, contacts)
    assert msg == MSG_ADDED
    assert contacts == expected_contacts


@pytest.mark.parametrize(
    "args, expected_substr",
    [
        (["John"], MSG_ENTER_NAME_PHONE),         
        (["John", "123-abc-456"], "Phone"),    
        ([], MSG_ENTER_NAME_PHONE),
    ],
    ids=["no_phone","letters_in_phone","no_args"]
)
def test_add_contact_errors(args, expected_substr):
    contacts = {}
    msg = add_contact(args, contacts)  
    assert expected_substr in msg

#-------------------- change_contact tests ------------------------------
@pytest.mark.parametrize(
    "args, expected_contacts",
    [
        (["John", "+49 176 12345678"], {"John": "+4917612345678", "John Doe": "0677654321"}),
        (["John Doe", "(093) 123-45-67"], {"John": "+380441234567", "John Doe": "0931234567"}),
    ],
    ids=["normal_name","quoted_name_local"]
)
def test_change_contact_ok(args, expected_contacts):
    contacts = {
        "John": "+380441234567",
        "John Doe": "0677654321",
    }

    msg = change_contact(args, contacts)
    assert msg == MSG_UPDATED
    assert contacts == expected_contacts


@pytest.mark.parametrize(
    "args, expected_substr",
    [
        ([], MSG_ENTER_NAME_PHONE),
        (["Jon"], MSG_ENTER_NAME_PHONE),         
        (["Jon", "+380-67-765-43-21"], MSG_NOT_FOUND),         
        (["John", "123-abc-456"], "Phone"),    
    ],
    ids=["no_args", "no_phone","contact_not_found","letters_in_phone"]
)
def test_change_contact_errors(args, expected_substr):
    contacts = {
        "Maria": "+380441234567",
        "John": "0677654321",
    }
    msg = change_contact(args, contacts)
    assert expected_substr in msg

#-------------------- delete_contact tests ------------------------------
@pytest.mark.parametrize(
    "args, expected_contacts",
    [
        (["John"], {"John Doe": "0677654321"}),
        (["John Doe"], {"John": "+380441234567"}),
    ],
    ids=["normal_name","quoted_name_local"]
)
def test_delete_contact_ok(args, expected_contacts):
    contacts = {
        "John": "+380441234567",
        "John Doe": "0677654321",
    }

    msg = delete_contact(args, contacts)
    assert msg == MSG_DELETED
    assert contacts == expected_contacts


@pytest.mark.parametrize(
    "args, expected_substr",
    [
        ([], MSG_ENTER_NAME_PHONE),
        (["Jon", "+380-67-765-43-21"], MSG_ENTER_NAME_PHONE),         
        (["Jon"], MSG_NOT_FOUND),         
    ],
    ids=["no_args", "name_phone","contact_not_found"]
)
def test_delete_contact_errors(args, expected_substr):
    contacts = {
        "Maria": "+380441234567",
        "John": "0677654321",
    }
    msg = delete_contact(args, contacts)
    assert expected_substr in msg

#-------------------- show_phone tests ------------------------------
@pytest.mark.parametrize(
    "args, expected_msg",
    [
        (["John"], "[name]John[/name]: [phone]+380441234567[/phone]"),
        (["John Doe"], "[name]John Doe[/name]: [phone]0677654321[/phone]"),
    ],
    ids=["normal_name","quoted_name_local"]
)
def test_show_contact_ok(args, expected_msg):
    contacts = {
        "John": "+380441234567",
        "John Doe": "0677654321",
    }

    msg = show_phone(args, contacts)
    assert msg == expected_msg


@pytest.mark.parametrize(
    "args, expected_substr",
    [
        ([], MSG_ENTER_NAME_PHONE),
        (["Jon", "+380-67-765-43-21"], MSG_ENTER_NAME_PHONE),         
        (["Jon"], MSG_NOT_FOUND),         
    ],
    ids=["no_args", "name_phone","contact_not_found"]
)
def test_show_contact_errors(args, expected_substr):
    contacts = {
        "Maria": "+380441234567",
        "John": "0677654321",
    }
    msg = show_phone(args, contacts)
    assert expected_substr in msg

#-------------------- delete_all tests ------------------------------
@pytest.mark.parametrize(
    "args, expected_contacts",
    [
        (["all"], {}),
    ],
    ids=["not_empty_contacts"]
)
def test_delete_all_ok(args, expected_contacts):
    contacts = {
        "John": "+380441234567",
        "John Doe": "0677654321",
    }

    msg = delete_all(contacts)
    assert msg == MSG_DELETED_ALL
    assert contacts == expected_contacts


@pytest.mark.parametrize(
    "args, expected_substr",
    [
        (["all"], MSG_NOT_FOUND),         
    ],
    ids=["empty_contacts"]
)
def test_delete_all_errors(args, expected_substr):
    contacts = {}
    msg = delete_all(contacts)
    assert expected_substr in msg

#-------------------- parse_input tests ------------------------------
@pytest.mark.parametrize(
    "input_data, expected_output",
    [
        ("add John +380441234567", ("add", ["John", "+380441234567"])),
        (" change  John   +380441234567  ", ("change", ["John", "+380441234567"])),
        (" phone 'John Doe'", ("phone", ["John Doe"])),
    ],
    ids=["normal_input","extra_spaces","quoted_name"]
)
def test_parse_input_ok(input_data, expected_output):
    output = parse_input(input_data)
    assert output == expected_output

@pytest.mark.parametrize(
    "input_data",
    [
        ("ttt"),
        (""),
        ("delete all phones")
    ],
    ids=["wrong_command","empty_string","wrong_delete"]
)
def test_parse_input_errors(input_data):
    with pytest.raises(ValueError):
        parse_input(input_data)

#-------------------- process_line tests ------------------------------
contacts = {
    "John": "+380441234567",
    "John Doe": "0677654321",
}    

@pytest.mark.parametrize(
    "command, args, contacts, expected_output",
    [
        ("hello", [], contacts, (MSG_HELLO, False)),
        ("help", [], contacts, (MSG_HELP, False)),
        ("exit", [], contacts, (MSG_GOODBYE, True)),
        ("phone", ["John"], contacts, ("[name]John[/name]: [phone]+380441234567[/phone]", False)),
        ("add", ["John", "+380441234567"], contacts, (MSG_ADDED, False)),
        ("change", ["John", "+380441234567"], contacts, (MSG_UPDATED, False)),
        ("delete", ["John Doe"], contacts, (MSG_DELETED, False)),
        ("delete_all", [], contacts, (MSG_DELETED_ALL, False)),
    ],
    ids=["hello","help","exit","show_phone","add","change","delete","delete_all"]
)
def test_process_line_ok(command, args, contacts, expected_output):
    output = process_line(command, args, contacts)
    assert output == expected_output

@pytest.mark.parametrize(
    "command, args, contacts",
    [
        ("ttt", [], contacts),
        ("", [], contacts),
    ],
    ids=["wrong_command","empty_string"]
)
def test_process_line_errors(command, args, contacts):
    with pytest.raises(ValueError):
        process_line(command, args, contacts)


# -------------------- End of tests ------------------------------
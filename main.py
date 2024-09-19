from collections import UserDict
from datetime import datetime, timedelta
import re
import pickle

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        super().__init__(value)
        

class Phone(Field):
    def __init__(self, value):
        if not self.validate(value):
            raise ValueError("Invalid phone number format. Should start from 0 and be 10 digits")
        super().__init__(value)

    def validate(self, value):
        # Validating phone number and raising exception if number is not 10 digits
        return len(value) == 10 and value.isdigit()      
        
class Birthday(Field):
    def __init__(self, value):
        if not self.validate(value):
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)

    def validate(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
            return True
        except ValueError:
            return False   


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
        
    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))

    def remove_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                self.phones.remove(phone)

    def edit_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = new_phone
                return
        raise ValueError("Phone number not found")
        
    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None
    
    def add_birthday(self, new_birthday):
        self.birthday = Birthday(new_birthday)
            
    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"
        

class AddressBook(UserDict):

    # Adds new record to the address book
    def add_record(self, record):
        self.data[record.name.value] = record

    # Seaches for phone using name
    def find(self, name):
        return self.data.get(name, None)

    # Deletes phone
    def delete(self, name):
        if name in self.data:
            del self.data[name]

    # Check birthdays
    def get_upcoming_birthdays(self):
        today = datetime.now().date()
        upcoming_birthdays = []

        for record in self.data.values():
            if record.birthday:
                birthday_date = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
                birthday_this_year = birthday_date.replace(year=today.year)

                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                days_until_birthday = (birthday_this_year - today).days

                if 0 <= days_until_birthday <= 7:
                    congratulation_date = birthday_this_year

                    if congratulation_date.weekday() >= 5:  # Saturday or Sunday
                        congratulation_date += timedelta(days=(7 - congratulation_date.weekday()))

                    upcoming_birthdays.append({
                        "name": record.name.value,
                        "congratulation_date": congratulation_date.strftime("%Y.%m.%d")
                    })

        return upcoming_birthdays
    
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except KeyError as e:
            return f"Contact {e} not found."
        except IndexError:
            return "Invalid number of arguments."
        except Exception as e:
            return f"An error occurred: {e}"
    return inner

@input_error
def add_contact(args, book):
    if len(args) != 2:
        raise ValueError("Give me name and phone please.")
    name, phone = args
    record = book.find(name)
    if record:
        record.add_phone(phone)
        return "Phone added."
    else:
        record = Record(name)
        record.add_phone(phone)
        book.add_record(record)
        return "Contact added."

@input_error
def change_contact(args, book):
    if len(args) != 3:
        raise ValueError("Give me name, old phone and new phone please.")
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return "Phone updated."
    else:
        raise KeyError(name)

@input_error
def show_phone(args, book):
    if len(args) != 1:
        raise ValueError("Enter user name")
    name = args[0]
    record = book.find(name)
    if record:
        return '; '.join(phone.value for phone in record.phones)
    else:
        raise KeyError(name)

@input_error
def show_all(book):
    return '\n'.join(str(record) for record in book.values())

@input_error
def add_birthday(args, book):
    if len(args) != 2:
        raise ValueError("Give me name and birthday please.")
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday added."
    else:
        raise KeyError(name)

@input_error
def show_birthday(args, book):
    if len(args) != 1:
        raise ValueError("Enter user name")
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return f"{name}'s birthday: {record.birthday.value}"
    elif record:
        return f"{name} has no birthday set."
    else:
        raise KeyError(name)

@input_error
def birthdays(book):
    upcoming = book.get_upcoming_birthdays()
    if upcoming:
        return '\n'.join(f"{b['name']}: {b['congratulation_date']}" for b in upcoming)
    else:
        return "No upcoming birthdays in the next week."

def parse_input(user_input):
    cmd, *args = re.findall(r'\S+', user_input)
    cmd = cmd.strip().lower()
    return cmd, args

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            save_data(book) 
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
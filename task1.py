from collections import UserDict, defaultdict
from datetime import datetime, date, timedelta
import calendar


class InvalidPhoneNumberError(ValueError):
    def __init__(self, message):
        super().__init__(message)


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if len(value) != 10 or not value.isdigit():
            raise InvalidPhoneNumberError("Phone number must have 10 digits")
        super().__init__(value)


class Record:
    def __init__(self, name: str, phone: str):
        self.name = Name(name)
        self.phone = Phone(phone)
        self.birthday = None

    def add_birthday(self, birthday: str):
        self.birthday = datetime.strptime(birthday, "%d.%m.%Y").date()

        return None

    def update_phone(self, new_phone_number: str):
        self.phone = Phone(new_phone_number)

    def __str__(self):
        return f"Contact name: {self.name.value}, phone: {self.phone.value}"


class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name: str) -> Record:
        return self[name]

    def delete(self, name: str):
        self.data.pop(name)

    def get_birthdays_per_week(self):
        upcoming_birthdays = defaultdict(list)
        for name, record in self.data.items():
            birthday: date = record.birthday
            if birthday is None:
                continue

            # Determine the user's next birthday
            today = datetime.today().date()

            try:
                next_birthday = birthday.replace(year=today.year)

                if next_birthday <= today:
                    next_birthday = next_birthday.replace(
                        year=next_birthday.year + 1)
            except ValueError:
                # Handle the 29 February problem. For simplicity ignore such users
                continue

            # Determine the date to congratulate (move to Monday if the birthday is on a weekend)
            date_to_congratulate = next_birthday

            if date_to_congratulate.weekday() in {5, 6}:
                days_until_monday = 7 - next_birthday.weekday()
                date_to_congratulate = date_to_congratulate + \
                    timedelta(days=days_until_monday)

            # Skip if the date to congratulate is more than 7 days away
            if (date_to_congratulate - today).days > 7:
                continue

            # Add a record to the collection
            weekday_to_congratulate = date_to_congratulate.weekday()
            upcoming_birthdays[weekday_to_congratulate].append(name)

        return upcoming_birthdays


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except InvalidPhoneNumberError as e:
            return "Invalid phone number."
        except ValueError:
            return "Invalid parameters."
        except KeyError:
            return "A contact with that name doesn't exist."

    return inner


def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


@input_error
def add_contact(args: list[str], book: AddressBook):
    name, phone = args
    book.add_record(Record(name, phone))
    return "Contact added."


@input_error
def change_contact(args: list[str], book: AddressBook):
    name, phone = args

    record = book.find(name)
    record.update_phone(phone)

    return "Contact changed."


@input_error
def show_phone(args: list[str], book: AddressBook):
    name, = args
    record = book.find(name)
    return record.phone.value


@input_error
def add_birthday(args: list[str], book: AddressBook):
    name, birthday = args
    record = book.find(name)
    record.add_birthday(birthday)

    return "Birthday added."


@input_error
def show_birthday(args: list[str], book: AddressBook):
    name, = args
    record = book.find(name)
    return record.birthday


def main():
    book = AddressBook()

    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
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
            print("|{:^20}|{:^20}|".format('Contact name', 'Phone number'))
            for record in book.values():
                print("|{:^20}|{:^20}|".format(record.name.value, record.phone.value))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            upcoming_birthdays = book.get_birthdays_per_week()

            weekday = datetime.today().weekday()
            for _ in range(0, 7):
                weekday = (weekday + 1) % 7

                if weekday not in upcoming_birthdays:
                    continue

                day_name = calendar.day_name[weekday]

                print(f"{day_name}: {', '.join(upcoming_birthdays[weekday])}")
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()

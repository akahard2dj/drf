import random
import string
import re


def random_digit_and_number(length_of_value=7):
    choices = string.ascii_uppercase + string.digits + string.ascii_lowercase
    random_value = ''.join(random.SystemRandom().choice(choices) for _ in range(length_of_value))
    return random_value


def is_valid_email(email):
    # Simple Regex for syntax checking
    regex = '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$'

    # Email address to verify
    addressToVerify = str(email)

    # Syntax check
    match = re.match(regex, addressToVerify)
    if not match:
        return False

    return True
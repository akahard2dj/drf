import random
import string


def random_digit_and_number(length_of_value=7):
    choices = string.ascii_uppercase + string.digits + string.ascii_lowercase
    random_value = ''.join(random.SystemRandom().choice(choices) for _ in range(length_of_value))
    return random_value

from random import randint

from faker import Faker

fake = Faker()


def produce_valid_tags():
    """
    This is moved to shortcuts.py since we are using it
    mostly on every newsletter tests anyway
    """
    tags = ""
    to_insert = fake.words(nb=randint(1, 6))
    if to_insert:
        tags = ",".join(to_insert)
    return tags

from random import randint

from faker import Faker

fake = Faker()


def produce_fake_random_words_or_none():

    words = ""
    to_insert = fake.words(nb=randint(0, 6))
    if to_insert:
        words = ",".join(to_insert)
    return words

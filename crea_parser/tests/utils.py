from random import randint

from faker import Faker

fake = Faker()


def produce_list_of_owner_ship_type_ids():

    ownership_ids = []
    number_of_ownership_type_to_insert = randint(1, 17)

    index = 0
    while index < number_of_ownership_type_to_insert:
        id = randint(1, 17)

        if id not in ownership_ids:
            ownership_ids.append(id)
        index += 1

    return ownership_ids


def produce_list_of_parking_type_ids():

    parking_type_ids = []

    number_of_parking_type_to_insert = randint(1, 38)

    index = 0

    while index < number_of_parking_type_to_insert:
        id = randint(1, 38)

        if id not in parking_type_ids:
            parking_type_ids.append(id)
        index += 1

    return parking_type_ids

import random


def generate_account_number():
    # 12-digit account number
    return "10" + "".join([str(random.randint(0, 9)) for _ in range(10)])

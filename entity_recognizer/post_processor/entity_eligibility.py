import re


def check_email(value: str):
    return bool(re.match(r"[^@]+@[^@]+\.[^@]{2,}", value))


def check_link(value: str):
    return bool(re.match(r"(http|https)://[a-zA-Z0-9./?#-]+", value) or re.match(r"www\.[a-zA-Z0-9./?#-]+", value))


def check_phone(value: str):
    return bool(re.match(r"\+?(?:[0-9] ?){6,14}[0-9]", value))


def is_eligible_value(value: str, entity_type: str) -> bool:
    """
    Checks if given value is meaningful enough to be considered an entity
    :param value: value to check
    :param entity_type: type of entity
    :return: True if eligible, False otherwise
    """
    if not value:
        return False

    value = value.strip()

    if len(value) < 3:
        return False

    if value.isdigit():
        return False

    # count the number of distinct non-whitespace characters
    if len(set(value.replace(" ", "").replace("\n", "").replace("\t", ""))) < 3:
        return False

    # check type-specific rules
    if entity_type == "email":
        return check_email(value)
    if entity_type == "link":
        return check_link(value)
    if entity_type == "phone":
        return check_phone(value)

    return True

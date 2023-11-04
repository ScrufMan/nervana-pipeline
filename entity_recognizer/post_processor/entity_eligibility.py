def is_eligible_value(value: str) -> bool:
    """
    Checks if given value is meaningful enough to be considered an entity
    :param value: value to check
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
    if len(set(value.replace(" ", ""))) < 3:
        return False

    return True

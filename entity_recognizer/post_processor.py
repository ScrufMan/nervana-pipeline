import re

def find_phone_numbers(data, phones):
    matches = re.findall("\\+?[0-9]{8,14}|\+ *[0-9]{3} *[0-9]{3} *[0-9]{3} *[0-9]{3}", data)

    for match in matches:
        if match not in phones:
            # model has detected phone number without prefix
            if match[1:].strip() in phones:
                phones.remove(match[1:].strip())

            phones.append(match)

def find_btc_adresses(data):
    matches = re.findall("[13][a-km-zA-HJ-NP-Z1-9]{25,34}", data)
    return matches
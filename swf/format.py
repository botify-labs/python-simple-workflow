import constants


def wrap(message, max_length):
    if not message:
        return message

    if len(message) > max_length:
        return message[:max_length]

    return message


def reason(message):
    return wrap(message, constants.MAX_REASON_LENGTH)


def details(message):
    return wrap(message, constants.MAX_DETAILS_LENGTH)


def input(message):
    return wrap(message, constants.MAX_INPUT_LENGTH)


def result(message):
    return wrap(message, constants.MAX_RESULT_LENGTH)

import inflection


def get_action_string(func_name):
    return rstrip_word(inflection.camelize(func_name, False), 'Request')


def get_request_string(func_name):
    return rstrip_word(inflection.camelize(func_name), 'Request') + 'Request'


def rstrip_word(text, suffix):
    if not text.endswith(suffix):
        return text
    return text[:len(text)-len(suffix)]

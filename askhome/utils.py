import inflection


def get_action_string(func_name):
    """Transform function name to Alexa action"""
    return rstrip_word(inflection.camelize(func_name, False), 'Request')


def get_request_string(func_name):
    """Transform function name to Alexa request name"""
    return rstrip_word(inflection.camelize(func_name), 'Request') + 'Request'


def rstrip_word(text, suffix):
    """Strip suffix from end of text"""
    if not text.endswith(suffix):
        return text
    return text[:len(text)-len(suffix)]

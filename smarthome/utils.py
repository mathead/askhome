import inflection


class classproperty(property):
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()


def get_action_string(func_name):
    return _strip_end(inflection.camelize(func_name, False), 'Request')


def get_request_string(func_name):
    return _strip_end(inflection.camelize(func_name), 'Request') + 'Request'


def _strip_end(text, suffix):
    if not text.endswith(suffix):
        return text
    return text[:len(text)-len(suffix)]

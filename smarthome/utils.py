import inflection


class classproperty(property):
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()


def get_action_string(func_name):
    return inflection.camelize(func_name, False).rstrip("Request")


def get_request_string(func_name):
    return inflection.camelize(func_name).rstrip("Request") + "Request"

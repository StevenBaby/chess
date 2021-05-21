# coding=utf-8


class attrdict(dict):

    '''
    Use dict key as attribute if available
    '''

    def __init__(self, *args, **kwargs):
        super(attrdict, self).__init__(*args, **kwargs)
        self.__dict__ = self

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as e:
            raise AttributeError(e)

    @classmethod
    def loads(cls, value):
        if isinstance(value, dict):
            result = cls()
            result.update(value)
            for k, v in result.items():
                result[k] = cls.loads(v)

        elif isinstance(value, list):
            for index, item in enumerate(value):
                if type(item) in (list, dict):
                    value[index] = cls.loads(item)
            result = value
        else:
            result = value
        return result

    @classmethod
    def json_loads(cls, value):
        import json
        data = json.loads(value)
        return cls.loads(data)

# coding=utf-8
'''
(C) Copyright 2021 Steven;
@author: Steven kangweibaby@163.com
@date: 2021-05-31
'''


class attrdict(dict):

    '''
    Use dict key as attribute if available

    使用属性的方式来访问字典，比如，下面两种方式是等价的：

    attr = attrdict()

    attr.hello = 1
    attr['hello'] = 1

    这样做的好处就是，编程的时候，有随笔提示，效率要比在中括号里写字符串高好多。
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
        '''
        将一个普通字典转换成 attrdict
        '''

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
        '''
        将 json 转换成 attrdict
        '''

        import json
        data = json.loads(value)
        return cls.loads(data)

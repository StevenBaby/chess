# coding=utf-8

VERSION = '1.8.1'
__VERSION__ = VERSION


def increase():
    import os
    import re
    filename = os.path.abspath(__file__)
    with open(filename, encoding='utf8') as file:
        content = file.read()

    match = re.search(r"VERSION = '(\d+).(\d+).(\d+)'", content)
    old = f'{match.group(1)}.{match.group(2)}.{match.group(3)}'
    new = f'{match.group(1)}.{match.group(2)}.{int(match.group(3)) + 1}'

    content = content.replace(old, new)

    with open(filename, 'w', encoding='utf8') as file:
        file.write(content)

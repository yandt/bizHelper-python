from re import sub


def hump_to_underline(hump: str) -> str:
    """
    驼峰表达式转下划线式
    :param hump:输入字符串
    :return: 驼峰字符串
    """
    res = []
    for index, char in enumerate(hump):
        if char.isupper() and index != 0:
            res.append("_")
        res.append(char)
    return ''.join(res).lower()


def to_hump_case(string):
    """
    将下划线式转换为驼峰字符串
    :param string:
    :return:
    """
    string = sub(r"(_|-)+", " ", string).title().replace(" ", "")
    return string[0].lower() + string[1:]



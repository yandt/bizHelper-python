
def copy(source: object, target: object, ignore_fields: list = [], ignore_none: bool = True):
    """
    复制一个对象的值给本实例
    :param ignore_none: 是否忽略源对象中的空值字段
    :param target: 目标对象
    :param source: 源对象
    :param ignore_fields: 忽略的字段名列表
    :return:
    """
    for key in source.__dict__:
        if not hasattr(target, key):
            continue
        # print('%s:' % key, end='')
        if key.startswith('_') or (ignore_fields is not None and key in ignore_fields):
            # print('ignore field')
            continue
        source_value = getattr(source, key)
        if source_value is None and ignore_none:
            print('%s ignore none '% key)
            continue
        setattr(target, key, source_value)
        # print('copy success')

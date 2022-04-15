import re


def fastApiPathMatches(config_path: str, request_path: str):
    """
    FastApi配置路径与request path匹配
    :param config_path:
    :param request_path:
    :return:
    """
    if config_path == request_path:
        return True
    if request_path.startswith(config_path):
        return True
    patter = re.sub(r'\/', '\\/', config_path)
    patter = re.sub(r'\{\w+\}', '\\\\w+', patter)
    if re.match(patter, request_path) is None:
        return False
    return True


def umiRoutesPathMatches(config_path: str, menu_path: str):
    """
    Umi配置的Routes配置路径与request path匹配
    :param config_path:
    :param request_path:
    :return:
    """
    if config_path == menu_path:
        return True
    patter = re.sub(r'\/', '\\/', config_path)
    patter = re.sub(r'\:\w+', '\\\\w+', patter)
    if re.match(patter, menu_path) is None:
        return False
    return True

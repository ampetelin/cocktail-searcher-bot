import json
from typing import Dict, Any
from urllib.parse import urlparse, urlencode, parse_qsl


def add_query_params_in_url(url: str, query_params: Dict[str, Any]) -> str:
    """
    Добавляет параметры запроса в URL-адрес

    Args:
        url: URL-адрес
        query_params: параметры запроса
    """
    parsed_url = urlparse(url)
    parsed_url_query = dict(parse_qsl(parsed_url.query))

    query_params = {k: v for k, v in query_params.items() if v is not None}
    query_params = {k: (json.dumps(v) if isinstance(v, bool) else v) for k, v in query_params.items()}
    parsed_url_query.update(query_params)

    return parsed_url._replace(query=urlencode(parsed_url_query)).geturl()

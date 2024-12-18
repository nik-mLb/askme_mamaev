import json

def simple_app(environ, start_response):
    """WSGI-приложение, возвращающее данные в формате JSON"""
    status = '200 OK'
    response_headers = [
        ('Content-Type', 'application/json; charset=utf-8'),
    ]
    start_response(status, response_headers)

    # Получаем метод запроса
    request_method = environ.get("REQUEST_METHOD")

    # Получаем GET-параметры
    get_params = environ.get("QUERY_STRING", "")
    get_params_dict = {k: v for k, v in [param.split("=") for param in get_params.split("&")]} if get_params else {}

    # Получаем POST-параметры
    try:
        content_length = int(environ.get("CONTENT_LENGTH", 0))
    except ValueError:
        content_length = 0

    post_data = environ["wsgi.input"].read(content_length).decode("utf-8") if content_length > 0 else ""

    # Проверяем, является ли тело запроса JSON
    if post_data and environ.get("CONTENT_TYPE", "").startswith("application/json"):
        try:
            post_params_dict = json.loads(post_data)  # Десериализация JSON
        except json.JSONDecodeError:
            post_params_dict = {"error": "Invalid JSON"}
    else:
        # Если это не JSON, то обрабатываем как обычные параметры
        post_params_dict = {k: v for k, v in [param.split("=") for param in post_data.split("&")]} if post_data else {}

    # Формируем ответ в формате JSON
    response_data = {
        "method": request_method,
        "GET": get_params_dict,
        "POST": post_params_dict,
    }
    response_json = json.dumps(response_data, ensure_ascii=False)  # Преобразуем в JSON-строку
    response_bytes = response_json.encode("utf-8")  # Кодируем в байты

    return [response_bytes]

application = simple_app

#gunicorn --bind=0.0.0.0:8081 test_wsgi
#gunicorn -c gunicorn_conf.py askme_mamaev.wsgi
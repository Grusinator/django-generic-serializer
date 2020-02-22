from test_app.django_model_enum import DjangoModelEnum


class RequestType(DjangoModelEnum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    UPDATE = "UPDATE"

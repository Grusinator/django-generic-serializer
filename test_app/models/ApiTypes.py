from test_app.django_model_enum import DjangoModelEnum


class ApiTypes(DjangoModelEnum):
    OAUTH_REST = "OauthRest"
    OAUTH_GRAPHQL = "OauthGraphql"
    TOKEN_REST = "TokenRest"

from django.db import models
from jsonfield import JSONField

from generic_serializer import SerializableModel
from test_app.models import DataProvider


class OauthConfig(models.Model, SerializableModel):
    data_provider = models.OneToOneField(DataProvider, related_name="oauth_config", on_delete=models.CASCADE)
    authorize_url = models.TextField()
    access_token_url = models.TextField()
    client_id = models.TextField()
    client_secret = models.TextField()
    scope = JSONField()

    def __str__(self):
        return f"OAuth2:{self.data_provider.provider_name}"

    class Meta:
        app_label = 'test_app'

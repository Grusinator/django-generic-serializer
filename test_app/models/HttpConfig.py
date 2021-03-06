from collections import OrderedDict

from django.db import models
from jsonfield import JSONField

from generic_serializer import SerializableModel
from test_app.models import DataProvider


class HttpConfig(models.Model, SerializableModel):
    load_kwargs = {'object_pairs_hook': OrderedDict}

    data_provider = models.OneToOneField(DataProvider, related_name="http_config", on_delete=models.CASCADE)
    header = JSONField(null=True, blank=True, load_kwargs=load_kwargs)
    url_encoded_params = JSONField(null=True, blank=True, load_kwargs=load_kwargs)
    body_type = models.TextField(null=True, blank=True)
    body_content = models.TextField(null=True, blank=True)
    request_type = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"HTTP Config:{self.data_provider.provider_name}"

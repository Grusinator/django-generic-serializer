from rest_framework import serializers

from test_app.models import DataProvider
from test_app.serializers.EndpointSerializer import EndpointSerializer
from test_app.serializers.HttpConfigSerializer import HttpConfigSerializer
from test_app.serializers.OauthConfigSerializer import OauthConfigSerializer


class DataProviderSerializer(serializers.ModelSerializer):
    oauth_config = OauthConfigSerializer()
    http_config = HttpConfigSerializer()
    endpoints = EndpointSerializer(many=True)

    class Meta:
        model = DataProvider
        exclude = ["id"]

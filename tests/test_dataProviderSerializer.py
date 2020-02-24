import django
from django.test import TransactionTestCase

from generic_serializer.json_utils import JsonUtils
from test_app.models import DataProvider, OauthConfig
from test_app.serializers.DataProviderSerializer import DataProviderSerializer
from tests.mock_data_provider import MockDataProvider


class TestDataProviderSerializer(TransactionTestCase):

    @classmethod
    def setUpClass(cls):
        super(TestDataProviderSerializer, cls).setUpClass()
        django.setup()

    def test_serializing_provider_only(self):
        dp = DataProvider.objects.create(
            provider_name="dsfsd4"
        )

        data = DataProviderSerializer(dp).data
        data = JsonUtils.dump_and_load(data)
        expected = {'oauth_config': None, 'http_config': None, 'endpoints': [], 'icon_image_url': None,
                    'provider_name': 'dsfsd4', 'provider_url': None, 'api_endpoint': None}
        self.assertEqual(expected, data)

    def test_serializing_provider_and_oauth(self):
        dp = DataProvider.objects.create(
            provider_name="dsfsd4",
        )
        oauth = OauthConfig.objects.create(
            data_provider=dp,
            authorize_url="test"
        )
        data = DataProviderSerializer(dp).data
        data = JsonUtils.dump_and_load(data)
        expected = {
            'oauth_config': {'authorize_url': 'test', 'access_token_url': '', 'client_id': '', 'client_secret': '',
                             'scope': ''}, 'http_config': None, 'endpoints': [], 'icon_image_url': None,
            'provider_name': 'dsfsd4', 'provider_url': None, 'api_endpoint': None}
        self.assertEqual(expected, data)

    def test_serializing_provider_and_endpoints(self):
        dp = MockDataProvider.create_data_provider_with_endpoints()
        data = DataProviderSerializer(dp).data
        data = JsonUtils.dump_and_load(data)
        expected = {'oauth_config': None, 'http_config': None, 'endpoints': [
            {'endpoint_name': 'test1', 'endpoint_url': 'testurl', 'request_type': 'GET', 'api_type': 'OauthRest'},
            {'endpoint_name': 'test2', 'endpoint_url': 'testurl', 'request_type': 'GET', 'api_type': 'OauthRest'}],
                    'icon_image_url': None, 'provider_name': 'dsfsd4', 'provider_url': None, 'api_endpoint': None}
        self.assertEqual(expected, data)

    def test_deserializing_provider_and_endpoints(self):
        data = {'endpoints': [
            {'endpoint_name': 'test1', 'endpoint_url': 'testurl', 'request_type': 'GET', 'api_type': 'OauthRest'},
            {'endpoint_name': 'test2', 'endpoint_url': 'testurl', 'request_type': 'GET', 'api_type': 'OauthRest'}],
            'icon_image_url': None, 'provider_name': 'dsfsd4', 'provider_url': None, 'api_endpoint': None}
        serializer = DataProviderSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(data, serializer.validated_data)

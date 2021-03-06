import django
from django.test import TransactionTestCase

from generic_serializer import SerializableModelFilter
from test_app.models import DataProvider, OauthConfig
from tests.mock_data_provider import MockDataProvider


class TestSerializableModelSerialize(TransactionTestCase):

    @classmethod
    def setUpClass(cls):
        super(TestSerializableModelSerialize, cls).setUpClass()
        django.setup()

        cls.model = DataProvider
        cls.exclude_labels = (
            "dataprovideruser",
        )
        cls.data_provider_name = "data_provider"

    def test_serializing_provider_only(self):
        data_provider = self.model.objects.create(
            provider_name="dsfsd4"
        )
        from generic_serializer import SerializableModelFilter
        data = data_provider.serialize(filter=SerializableModelFilter(max_depth=0))
        expected = {'provider_name': 'dsfsd4', 'api_endpoint': None}
        self.assertDictEqual(expected, data)

    def test_serializing_provider_and_oauth(self):
        data_provider = self.model.objects.create(provider_name="dsfsd6")
        OauthConfig.objects.create(
            data_provider=data_provider,
            authorize_url="test",
            access_token_url="test.dk",
            client_id="123",
            client_secret="test",
            scope=['234', ]
        )
        filter = SerializableModelFilter(max_depth=1, exclude_labels=self.exclude_labels + ("endpoints", "http_config"))
        data = data_provider.serialize(filter=filter)

        expected = {'provider_name': 'dsfsd6', 'api_endpoint': None,
                    'oauth_config': {'authorize_url': 'test', 'access_token_url': 'test.dk', 'client_id': '123',
                                     'client_secret': 'test', 'scope': ['234']}}
        self.assertDictEqual(expected, data)

    def test_serializing_provider_and_endpoints(self):
        data_provider = MockDataProvider.create_data_provider_with_endpoints()

        from generic_serializer import SerializableModelFilter
        data = data_provider.serialize(
            filter=SerializableModelFilter(max_depth=2, exclude_labels=("dataprovideruser",),
                                           start_object_name="data_provider"))
        expected = {'provider_name': 'dsfsd4', 'api_endpoint': None, 'endpoints': [
            {'endpoint_name': 'test1', 'endpoint_url': 'testurl', 'api_type': 'OauthGraphql', 'request_type': 'GET'},
            {'endpoint_name': 'test2', 'endpoint_url': 'testurl', 'api_type': 'OauthGraphql', 'request_type': 'GET'}],
                    'http_config': None, 'oauth_config': None}
        self.assertEqual(expected, data)

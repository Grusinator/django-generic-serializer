import django
from django.db.models.fields.related_descriptors import ForwardManyToOneDescriptor
from django.test import TransactionTestCase
from rest_framework.serializers import SerializerMetaclass

from generic_serializer import SerializableModelFilter
from test_app.models import DataProvider


class TestSerializableModel(TransactionTestCase):

    @classmethod
    def setUpClass(cls):
        django.setup()
        cls.model = DataProvider

    def test_build_serializer(self):
        serializer = self.model._build_serializer(self.build_default_test_filter(max_depth=2))
        self.assertEqual(serializer.Meta.model, self.model)
        expected_fields = ['api_endpoint', 'provider_name', 'oauth_config', 'http_config', 'endpoints']
        self.assertEqual(expected_fields, serializer.Meta.fields)

        for name in ['endpoints', 'http_config', 'oauth_config']:
            self.assert_sub_serializer(name, serializer)

    def assert_sub_serializer(self, name, serializer):
        sub_serializer = getattr(serializer.Meta, name)
        self.assertIsInstance(sub_serializer, SerializerMetaclass)
        self.assertIsInstance(sub_serializer.Meta.model.data_provider, ForwardManyToOneDescriptor)
        return sub_serializer

    def test_build_serializer_exclude(self):
        serializer = self.model._build_serializer(self.build_default_test_filter(exclude_labels=('oauth_config',)))
        self.assertEqual(serializer.Meta.model, self.model)
        self.assertIn('endpoints', serializer.Meta.fields)
        self.assertIn('http_config', serializer.Meta.fields)
        self.assertFalse(hasattr(serializer, "oauth_config"))
        self.assertTrue(hasattr(serializer, "http_config"))
        self.assertTrue(hasattr(serializer, "endpoints"))

    def test_build_serializer_depth_0(self):
        serializer = self.model._build_serializer(self.build_default_test_filter(max_depth=0))
        self.assertTrue(hasattr(serializer, "Meta"))
        self.assertFalse(hasattr(serializer, "oauth_config"))
        self.assertFalse(hasattr(serializer, "http_config"))
        self.assertFalse(hasattr(serializer, "endpoints"))

    def test_build_serializer_depth_1(self):
        serializer = self.model._build_serializer(self.build_default_test_filter(max_depth=1))
        for name in ['endpoints', 'http_config', 'oauth_config']:
            sub_serializer = self.assert_sub_serializer(name, serializer)
            if name is "endpoints":
                self.assertFalse(hasattr(sub_serializer, "data_fetches"))

    def test_build_serializer_depth_2(self):
        serializer = self.model._build_serializer(self.build_default_test_filter(max_depth=2))
        for name in ['endpoints', 'http_config', 'oauth_config']:
            sub_serializer = self.assert_sub_serializer(name, serializer)
            if name is "endpoints":
                self.assertTrue(hasattr(sub_serializer, "data_fetches"))

    def build_default_test_filter(self, max_depth=0, exclude_labels=(), start_object_name="data_provider"):
        default_exclude = ("data_provider_node", "dataprovideruser")
        return SerializableModelFilter(
            max_depth=max_depth,
            exclude_labels=exclude_labels + default_exclude,
            start_object_name=start_object_name)

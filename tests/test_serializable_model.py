import django
from django.test import TransactionTestCase
from model_bakery import baker

from generic_serializer import SerializableModelFilter
from test_app.models import TestModel3, TestModel1, TestModel2


class TestSerializableModel(TransactionTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        django.setup()

    def test_serialize(self):
        obj = TestModel3.objects.create(
            text="dummy",
        )
        data = obj.serialize()
        expected = {'text': 'dummy'}
        self.assertEqual(data, expected)

    def test_serialize_related(self):
        obj3 = TestModel3.objects.create(
            text="dummy",
        )
        obj2 = TestModel2.objects.create(
            text="dummy",
            test_model3=obj3
        )
        filter = SerializableModelFilter(max_depth=2, start_object_name="test_model1")
        data = obj2.serialize(filter=filter)
        self.assertIsNotNone(data["test_model3"]["text"])

    def test_serialize_baker(self):
        obj = baker.make(TestModel3, text="dummy")
        data = obj.serialize()
        expected = {'text': 'dummy'}
        self.assertEqual(data, expected)

    def test_serialize_related_baker(self):
        filter = SerializableModelFilter(max_depth=2, start_object_name="test_model1")
        obj = baker.make(TestModel1, make_m2m=True)
        data = obj.serialize(filter=filter)
        self.assertIsNotNone(data["test_model2"]["test_model3"]["text"])

    def test_deserialize(self):
        assert False

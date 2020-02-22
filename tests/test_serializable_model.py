import django
from django.test import TransactionTestCase
from model_bakery import baker

from test_app.models import TestModel3, TestModel1


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

    def test_serialize_baker(self):
        obj = baker.make(TestModel3, text="dummy")
        data = obj.serialize()
        expected = {'text': 'dummy'}
        self.assertEqual(data, expected)

    def test_serialize_related(self):
        # filter = SerializableModelFilter()
        obj = baker.make(TestModel1, make_m2m=True)
        data = obj.serialize()
        self.assertIsNotNone(data["test_model2"]["test_model3"]["text"])

    def test_deserialize(self):
        assert False

from django.db import models

# Create your models here.
from generic_serializer import SerializableModel


class TestModel3(models.Model, SerializableModel):
    text = models.TextField()


class TestModel2(models.Model, SerializableModel):
    text = models.TextField()
    test_model3 = models.ForeignKey(TestModel3, on_delete=models.CASCADE)


class TestModel1(models.Model, SerializableModel):
    text = models.TextField()
    test_model2 = models.ForeignKey(TestModel2, on_delete=models.CASCADE)

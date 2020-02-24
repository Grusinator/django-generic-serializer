import logging

from django.db.models import TextField, IntegerField, FloatField, BooleanField, ForeignKey, OneToOneField, ManyToOneRel, \
    OneToOneRel
from django.db.models.fields.related_descriptors import ReverseOneToOneDescriptor, ReverseManyToOneDescriptor
from jsonfield import JSONField
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer, JSONField as JSONSerializerField

from generic_serializer.json_utils import JsonUtils
from .serializable_model_filter import SerializableModelFilter

logger = logging.getLogger(__name__)

MODEL = "model"
META = "Meta"
FIELDS = "fields"

many_to_one_relation_types = (ForeignKey, ManyToOneRel)
one_to_one_relation_types = (OneToOneField, OneToOneRel)
relation_types = many_to_one_relation_types + one_to_one_relation_types
attribute_types = (TextField, IntegerField, FloatField, BooleanField, JSONField)
CUSTOM_FIELDS = {JSONField: JSONSerializerField, }
default_filter = SerializableModelFilter()


class SerializableModel:
    def get_model_name(self):
        return self._meta.model_name

    def serialize(self, filter: SerializableModelFilter = default_filter):
        if not filter.current_object_name:
            # TODO ._meta.model_name is not the correct property. fix.
            logger.debug(f"using default model name as starting name: {self.get_model_name()}")
            filter.current_object_name = self.get_model_name()
        Serializer = type(self)._build_serializer(filter)
        serializer = Serializer(self)
        return JsonUtils.validate(serializer.data)

    @classmethod
    def deserialize(cls, data, filter: SerializableModelFilter):
        deserialized_object = cls._deserialize_to_objects(data, filter)
        return deserialized_object

    @classmethod
    def _deserialize_to_objects(cls, data, filter: SerializableModelFilter):
        # This is not so nice, should maybe be refactored. It is in order to be able to only create the related
        # objects serializers that actually should be serialized
        filter.data = data
        Serializer = cls._build_serializer(filter)
        serializer = Serializer(data=data)
        if not serializer.is_valid():
            raise ValidationError(f"could not deserialize, due to error: {serializer.errors}")
        serialized_object = serializer.save()
        return serialized_object

    @classmethod
    def _build_serializer(cls, filter: SerializableModelFilter):
        properties = cls._build_properties(filter)
        serializer = type(cls.__name__ + "Serializer", (ModelSerializer,), properties)
        return serializer

    @classmethod
    def _build_properties(cls, filter: SerializableModelFilter) -> dict:
        # each property must contain the serializer class for any related object so it is here the recursive filtering
        # is handled
        properties = {META: cls._build_meta_class(filter)}
        custom_field_properties = cls._build_custom_field_properties(filter)
        properties.update(custom_field_properties)
        properties = cls._add_relations_to_properties(properties, filter)
        properties = cls._add_create_method_to_properties(properties)
        return properties

    @classmethod
    def _build_relation_serializers(cls, relation_names, filter) -> dict:
        return {name: cls._try_build_relation_serializer_instance(name, filter) for name in relation_names}

    @classmethod
    def _try_build_relation_serializer_instance(cls, relation_name, filter):
        filter.step_into(relation_name)
        related_object = cls._get_related_object_by_property_name(relation_name)
        try:
            Serializer = related_object._build_serializer(filter)
        except Exception as e:
            logger.warning(f"could not create related serializer object with name: {relation_name}")
        else:
            return Serializer(many=cls._is_related_object_many(relation_name), required=False)
        finally:
            filter.step_out()

    @classmethod
    def _is_related_object_many(cls, property_name):
        return type(cls._meta.get_field(property_name)) in many_to_one_relation_types

    @classmethod
    def _get_related_object_by_property_name(cls, property_name):
        return cls._meta.get_field(property_name).related_model

    @classmethod
    def _build_meta_class(cls, filter):
        meta_properties = {
            MODEL: cls,
            FIELDS: cls._get_all_attribute_names(filter)
        }
        return type(META, (), meta_properties)

    @classmethod
    def _get_all_model_relations_names(cls, filter: SerializableModelFilter) -> list:
        names = cls._get_all_field_names_of_type(relation_types)
        names = filter.apply_relation_filter(names)
        return names

    @classmethod
    def _get_all_attribute_names(cls, filter):
        names = cls._get_all_field_names_of_type(attribute_types)
        return filter.apply_property_filter(names)

    @classmethod
    def _get_all_field_names_of_type(cls, types) -> list:
        return [field.name for field in cls._meta.get_fields() if isinstance(field, types)]

    @classmethod
    def _add_relations_to_properties(cls, properties, filter: SerializableModelFilter):
        relation_names = cls._get_all_model_relations_names(filter)
        properties[META].fields += relation_names
        properties.update(cls._build_relation_serializers(relation_names, filter))
        return properties

    @classmethod
    def _build_custom_field_properties(cls, filter):
        # custom filed properties is need for custom fields such as JSONField, that is not build in DRF
        custom_field_properties = {}
        for ModelField, SerializerField in CUSTOM_FIELDS.items():
            names = cls._get_all_field_names_of_type(ModelField)
            names = filter.apply_property_filter(names)
            custom_field_properties.update({name: SerializerField() for name in names})
        return custom_field_properties

    @classmethod
    def create(cls, validated_data):
        properties = cls._get_properties_from_data(validated_data)
        base_instance = cls.objects.create(**properties)
        cls._create_related_objects(base_instance, validated_data)
        return base_instance

    @classmethod
    def _create_related_objects(cls, base_instance, validated_data):
        relations = cls._get_relations_from_data(validated_data)
        for relation_name, relation_data in relations.items():
            relation_object = cls._get_relation_object(relation_name)
            parrent_data = cls._create_parrent_data(base_instance, relation_name)
            if not cls._is_related_object_many(relation_name):
                relation_data = [relation_data]
            for relation_data_element in relation_data:
                relation_object.objects.create(**relation_data_element, **parrent_data)

    @classmethod
    def _create_parrent_data(cls, base_instance, relation_name):
        to_parrent_related_name = cls._get_related_name(relation_name)
        parrent_info = {to_parrent_related_name: base_instance}
        return parrent_info

    @classmethod
    def _add_create_method_to_properties(cls, properties):
        properties["create"] = cls.create
        return properties

    @classmethod
    def _get_properties_from_data(cls, data):
        names = cls._get_all_field_names_of_type(attribute_types)
        return {name: val for name, val in data.items() if name in names}

    @classmethod
    def _get_relations_from_data(cls, data) -> dict:
        names = cls._get_all_field_names_of_type(relation_types)
        return {name: val for name, val in data.items() if name in names}

    @classmethod
    def _get_relation_object(cls, relation_name):
        return cls._get_related_field(relation_name).model

    @classmethod
    def _get_related_name(cls, relation_name):
        return cls._get_related_field(relation_name).name

    @classmethod
    def _get_related_field(cls, relation_name):
        related_object = getattr(cls, relation_name)
        # if isinstance(related_object, (OneToOneRel, ManyToOneRel)):
        #     return related_object.related.field
        # elif isinstance(related_object, (OneToOneField, ForeignKey)):
        #     return related_object.field
        if isinstance(related_object, (ReverseOneToOneDescriptor,)):
            return related_object.related.field
        elif isinstance(related_object, (ReverseManyToOneDescriptor,)):
            return related_object.field
        else:
            raise AttributeError(f"unknown relation type: {type(related_object)}")

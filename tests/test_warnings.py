from unittest import mock

from django.db import models
from rest_framework import serializers, mixins, viewsets
from rest_framework.decorators import action

from drf_spectacular.openapi import AutoSchema
from tests import generate_schema


@mock.patch('rest_framework.settings.api_settings.DEFAULT_SCHEMA_CLASS', AutoSchema)
def test_serializer_name_reuse(warnings):
    from rest_framework import routers
    from drf_spectacular.openapi import SchemaGenerator
    router = routers.SimpleRouter()

    def x1():
        class XSerializer(serializers.Serializer):
            uuid = serializers.UUIDField()

        return XSerializer

    def x2():
        class XSerializer(serializers.Serializer):
            integer = serializers.IntegerField

        return XSerializer

    class X1Viewset(mixins.ListModelMixin, viewsets.GenericViewSet):
        serializer_class = x1()

    router.register('x1', X1Viewset, basename='x1')

    class X2Viewset(mixins.ListModelMixin, viewsets.GenericViewSet):
        serializer_class = x2()

    router.register('x2', X2Viewset, basename='x2')

    generator = SchemaGenerator(patterns=router.urls)
    generator.get_schema(request=None, public=True)


@mock.patch('rest_framework.settings.api_settings.DEFAULT_SCHEMA_CLASS', AutoSchema)
def test_no_queryset_warn(capsys):
    class X1Serializer(serializers.Serializer):
        uuid = serializers.UUIDField()

    class X1Viewset(viewsets.ReadOnlyModelViewSet):
        serializer_class = X1Serializer

    generate_schema('x1', X1Viewset)
    assert 'no queryset' in capsys.readouterr().err


@mock.patch('rest_framework.settings.api_settings.DEFAULT_SCHEMA_CLASS', AutoSchema)
def test_path_param_not_in_model(capsys):
    class M3(models.Model):
        pass

    class XSerializer(serializers.Serializer):
        uuid = serializers.UUIDField()

    class XViewset(viewsets.ReadOnlyModelViewSet):
        serializer_class = XSerializer
        queryset = M3.objects.none()

        @action(detail=True, url_path='meta/(?P<ephemeral>[^/.]+)', methods=['POST'])
        def meta_param(self, request, ephemeral, pk):
            pass

    generate_schema('x1', XViewset)
    assert 'no such field' in capsys.readouterr().err
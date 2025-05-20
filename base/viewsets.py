from collections.abc import Iterable

from django.core.exceptions import ImproperlyConfigured
from rest_framework import viewsets
from rest_framework.permissions import BasePermission
from rest_framework.serializers import BaseSerializer

from base.generics import GenericAPIView
from base.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)


class GenericViewSet(viewsets.ViewSetMixin, GenericAPIView):
    action_permission_classes: dict[str, type[BasePermission] | Iterable[type[BasePermission]]] | None = None
    request_action_serializer_classes: dict[str, type[BaseSerializer]] | None = None
    response_action_serializer_classes: dict[str, type[BaseSerializer]] | None = None

    def get_permission_classes_or_none(self):
        if self.action_permission_classes:
            permission_classes = self.action_permission_classes.get(self.action)

            if permission_classes is None and self.action == "partial_update":
                permission_classes = self.action_permission_classes.get("update")

            return permission_classes
        return None

    def get_permissions(self):
        permissions = []

        permission_classes = self.get_permission_classes_or_none()

        if permission_classes is not None:
            if isinstance(permission_classes, Iterable):
                for permission_class in permission_classes:
                    permissions.append(permission_class())
            else:
                permissions.append(permission_classes())

        return permissions or super().get_permissions()

    def get_request_serializer_class_or_none(self) -> type[BaseSerializer] | None:
        serializer_class = None

        if self.request_action_serializer_classes:
            serializer_class = self.request_action_serializer_classes.get(self.action)
            if serializer_class is None and self.action == "partial_update":
                serializer_class = self.request_action_serializer_classes.get("update")

        if serializer_class is None:
            return super().get_request_serializer_class_or_none()

        return serializer_class

    def raise_request_serializer_error(self):
        raise ImproperlyConfigured(
            f"{self.__class__.__name__} should properly configure "
            "`request_action_serializer_classes` attribute"
        )

    def get_response_serializer_class_or_none(self) -> type[BaseSerializer] | None:
        serializer_class = None

        if self.response_action_serializer_classes:
            serializer_class = self.response_action_serializer_classes.get(self.action)

            if serializer_class is None and self.action == "partial_update":
                serializer_class = self.response_action_serializer_classes.get("update")

        if serializer_class is None:
            return super().get_response_serializer_class_or_none()

        return serializer_class

    def raise_response_serializer_error(self):
        raise ImproperlyConfigured(
            f"{self.__class__.__name__} should properly configure "
            "`response_action_serializer_classes` attribute"
        )

    def raise_serializer_error(self):
        raise ImproperlyConfigured(
            f"{self.__class__.__name__} should properly configure one of these attributes: "
            f"`response_action_serializer_classes`, `serializer_class`"
        )


class ReadOnlyModelViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    """
    A viewset that provides default `list()` and `retrieve()` actions.
    """

    pass


class ModelViewSet(
    CreateModelMixin,
    RetrieveModelMixin,
    ListModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    """
    A viewset that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions.
    """

    pass

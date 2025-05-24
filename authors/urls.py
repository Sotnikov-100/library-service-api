from django.urls import path, include
from rest_framework.routers import DefaultRouter
from authors.views import AuthorViewSet


router = DefaultRouter()
router.register(r"", AuthorViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "authors"

from django.contrib import admin
from django.conf import settings

from django.urls import path
from django.conf.urls.static import static

from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)
from core.views import Video_process, RegisterView, CustomLoginView

urlpatterns = [
    path("signup", RegisterView.as_view(), name="register"),
    path("signin", CustomLoginView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("upload", Video_process.as_view(), name="file_upload"),
]

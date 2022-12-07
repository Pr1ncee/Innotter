from django.urls import path, include
from rest_framework import routers

from user import views

app_name = 'user'

router = routers.DefaultRouter()
router.register(r'users', views.AdminUserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls))
]
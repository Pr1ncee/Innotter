from django.urls import path, include
from rest_framework import routers

from . import views

app_name = 'posts'

router = routers.DefaultRouter()
router.register(r'pages', views.PagesViewSet, basename='pages')
router.register(r'posts', views.PostsViewSet, basename='posts')

urlpatterns = [
    path('', include(router.urls))
]

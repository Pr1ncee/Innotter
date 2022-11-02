from django.urls import path, include
from rest_framework import routers

from . import views

app_name = 'posts'

router = routers.DefaultRouter()
router.register(r'api/v1/pages', views.PagesViewSet, basename='pages')
router.register(r'api/v1/mypages', views.MyPagesViewSet, basename='mypages')
router.register(r'api/v1/posts', views.PostsViewSet, basename='posts')
router.register(r'api/v1/myposts', views.MyPostsViewSet, basename='myposts')
router.register(r'api/v1/users', views.AdminUserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls))
]

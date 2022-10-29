from django.urls import path, include
from rest_framework import routers

from . import views

app_name = 'posts'

router = routers.DefaultRouter()
router.register(r'pages', views.CreateListPageViewSet)
router.register(r'pages/edit', views.UpdatePageViewSet)
router.register(r'pages/delete-tag', views.DestroyTagViewSet)
router.register(r'pages/follow_requests', views.RetrieveFollowRequestsViewSet)
router.register(r'posts', views.CreateListPostViewSet)
router.register(r'posts/edit', views.UpdateDestroyPostViewSet)
router.register(r'posts/liked', views.ListLikedPostViewSet)

urlpatterns = [
    path('', include(router.urls))
]

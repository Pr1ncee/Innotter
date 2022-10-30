from django.urls import path, include
from rest_framework import routers

from . import views

app_name = 'posts'

router = routers.DefaultRouter()
router.register(r'pages', views.ListAllPagesViewSet, basename='all-pages')
router.register(r'pages/follow', views.RetrieveUpdatePageFollowersViewSet, basename='follow-page')
router.register(r'pages/mine/follow/accept', views.AcceptPageFollowRequestViewSet, basename='accept-request')
router.register(r'pages/mine/follow/deny', views.DenyPageFollowRequestViewSet, basename='deny-request')
router.register(r'pages/mine/create', views.CreateListPageViewSet, basename='page')
router.register(r'pages/mine/edit', views.UpdatePageViewSet, basename='page')
router.register(r'pages/mine/delete-tag', views.DestroyPageTagViewSet, basename='page')
router.register(r'posts', views.ListAllPostsViewSet, basename='all-posts')
router.register(r'posts/like', views.RetrieveUpdatePostLikeViewSet, basename='like-post')
router.register(r'posts/mine', views.CreateListPostViewSet, basename='post')
router.register(r'posts/mine/edit', views.UpdateDestroyPostViewSet, basename='post')
router.register(r'posts/mine/liked', views.ListLikedPostViewSet, basename='post')
router.register(r'manager/pages', views.ManagerPageViewSet, basename='manager-pages')
router.register(r'manager/posts', views.ManagerPostViewSet, basename='manager-posts')
router.register(r'users/ban', views.AdminUserViewSet, basename='admin-ban')

urlpatterns = [
    path('', include(router.urls))
]

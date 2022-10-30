from django.urls import path, include
from rest_framework import routers

from . import views

app_name = 'posts'

router = routers.DefaultRouter()
router.register(r'pages', views.ListAllPagesViewSet, basename='page-all')
router.register(r'pages/follow', views.RetrieveUpdatePageFollowersViewSet, basename='page-follow')
router.register(r'pages/mine/follow/accept', views.AcceptPageFollowRequestViewSet, basename='page-accept-request')
router.register(r'pages/mine/follow/deny', views.DenyPageFollowRequestViewSet, basename='page-deny-request')
router.register(r'pages/mine/create', views.ListCreatePageViewSet, basename='page-create')
router.register(r'pages/mine/edit', views.RetrieveUpdateDestroyPageViewSet, basename='page-update')
router.register(r'pages/mine/delete-tag', views.RetrieveDestroyPageTagViewSet, basename='page-delete-tag')
router.register(r'posts', views.ListAllPostsViewSet, basename='post-all')
router.register(r'posts/feed', views.ListFollowedMyPostsViewSet, basename='post-feed')
router.register(r'posts/like', views.RetrieveUpdatePostLikeViewSet, basename='post-like')
router.register(r'posts/mine/create', views.CreateListPostViewSet, basename='post-create')
router.register(r'posts/mine/edit', views.UpdateDestroyPostViewSet, basename='post-update')
router.register(r'posts/mine/liked', views.ListLikedPostViewSet, basename='post-list-liked')
router.register(r'manager/pages', views.ManagerPageViewSet, basename='manager-pages')
router.register(r'manager/posts', views.ManagerPostViewSet, basename='manager-posts')
router.register(r'users/ban', views.AdminUserViewSet, basename='admin-ban')

urlpatterns = [
    path('', include(router.urls))
]

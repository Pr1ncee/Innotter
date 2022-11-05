from django.contrib import admin
from django.urls import path, include
from rest_framework import routers


router = routers.DefaultRouter()
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('authorization.urls')),
    path('api/v1/', include('posts.urls')),
    path('api/v1/', include('user.urls')),
]

urlpatterns += router.urls

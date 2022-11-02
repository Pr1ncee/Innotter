from django.urls import path
from rest_framework import routers

from . import views


app_name = 'authorization'

router = routers.DefaultRouter()

urlpatterns = [
    path('api/vi/auth/signin/', views.UserSigninApi.as_view(), name='signin'),
    path('api/vi/auth/signup/', views.UserSignupApi.as_view(), name='signup'),
    path('api/vi/auth/signout/', views.UserSignoutApi.as_view(), name='signout'),
    path('api/vi/auth/token/refresh/', views.UserTokenRefreshApi.as_view(), name='token_refresh'),
    path('api/vi/auth/token/verify/', views.UserTokenVerifyApi.as_view(), name='token_verify'),
]

urlpatterns += router.urls

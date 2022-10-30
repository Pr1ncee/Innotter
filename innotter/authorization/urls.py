from django.urls import path
from rest_framework import routers

from . import views


app_name = 'authorization'

router = routers.DefaultRouter()

urlpatterns = [
    path('authentication/signin/', views.UserSigninApi.as_view(), name='signin'),
    path('authentication/signup/', views.UserSignupApi.as_view(), name='signup'),
    path('authentication/signout/', views.UserSignoutApi.as_view(), name='signout'),
    path('authentication/token/refresh/', views.UserTokenRefreshApi.as_view(), name='token_refresh'),
    path('authentication/token/verify/', views.UserTokenVerifyApi.as_view(), name='token_verify'),
]

urlpatterns += router.urls

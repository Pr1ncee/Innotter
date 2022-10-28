from django.urls import path
from rest_framework import routers

from . import views


app_name = 'authorization'

router = routers.DefaultRouter()

urlpatterns = [
    path('authentication/signin/', views.SigninView.as_view(), name='signin'),
    path('authentication/signup/', views.SignupView.as_view(), name='signup'),
    path('authentication/signout/', views.SignoutView.as_view(), name='signout'),
    path('authentication/token/refresh/', views.TokenRefresh.as_view(), name='token_refresh'),
    path('authentication/token/verify/', views.TokenVerify.as_view(), name='token_verify'),
]

urlpatterns += router.urls

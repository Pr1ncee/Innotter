from django.urls import path
from rest_framework import routers

from . import views


app_name = 'authorization'

router = routers.DefaultRouter()

urlpatterns = [
    path('authentication/token/', views.ObtainTokens.as_view(), name='tokens_obtain'),
    path('authentication/token/refresh/', views.TokenRefresh.as_view(), name='token_refresh'),
    path('authentication/token/verify/', views.TokenVerify.as_view(), name='token_verify'),
    path('signin/', views.LoginView.as_view(), name='signin'),
    path('signup/', views.RegisterView.as_view(), name='signup'),
]

urlpatterns += router.urls

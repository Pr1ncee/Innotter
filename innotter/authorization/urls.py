from django.urls import path
from rest_framework import routers

from . import views


app_name = 'authorization'

router = routers.DefaultRouter()

urlpatterns = [
    path('obtain-tokens/', views.ObtainTokensView.as_view(), name='obtain_tokens'),
    path('signup/', views.UserSignupView.as_view(), name='signup'),
    path('token/refresh/', views.UserTokenRefreshView.as_view(), name='token_refresh'),
<<<<<<< HEAD
=======
    path('token/verify/', views.UserTokenVerifyView.as_view(), name='token_verify'),
>>>>>>> ded63ef5c5337092a4cb3d01aba73b6a9d0f21fd
]

urlpatterns += router.urls

from django.urls import path
from rest_framework import routers

from authorization import views


app_name = 'authorization'

router = routers.DefaultRouter()

urlpatterns = [
    path('obtain-tokens/', views.ObtainTokensView.as_view(), name='obtain_tokens'),
    path('signup/', views.UserSignupView.as_view(), name='signup'),
    path('token/refresh/', views.UserTokenRefreshView.as_view(), name='token_refresh'),
]

urlpatterns += router.urls

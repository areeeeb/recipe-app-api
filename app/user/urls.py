from django.urls import path

from .views import CreateUserView, GenerateTokenView


app_name = 'user'

urlpatterns = [
    path('create/', CreateUserView.as_view(), name='create'),
    path('token/', GenerateTokenView.as_view(), name='token'),
]

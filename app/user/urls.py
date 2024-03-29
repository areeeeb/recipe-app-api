from django.urls import path

from .views import CreateUserView, GenerateTokenView, ManageUserView


app_name = 'user'

urlpatterns = [
    path('create/', CreateUserView.as_view(), name='create'),
    path('token/', GenerateTokenView.as_view(), name='token'),
    path('me/', ManageUserView.as_view(), name='me'),
]

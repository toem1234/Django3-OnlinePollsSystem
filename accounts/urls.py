from django.urls import path,include
from . import views

app_name="accounts"
urlpatterns = [
    path('signup/',views.SignupView.as_view(), name='SignupView'),
    path('login/',views.LoginView.as_view(), name='LoginView'),
    path('logout/',views.LogoutView.as_view(), name="LogoutView"),
    path('info/',views.InfoView.as_view(),name='InfoView'),

]
from django.urls import path,include
from . import views
from .api import PollList,PollDetail

app_name="polls"
urlpatterns = [
    path('create/',views.CreateView.as_view(), name='CreateView'),
    path('detail/<int:question_id>',views.DetailView.as_view(), name='DetailView'),
    path('edit/<int:question_id>',views.EditView.as_view(), name="EditView"),
    path('',views.IndexView.as_view(),name='IndexView'),
    path('own/',views.OwnView.as_view(),name='OwnView'),
    path('results/<int:question_id>',views.ResultView.as_view(),name='ResultView'),

    
    path('api/poll/',PollList.as_view(),name='PollListAPIView'),
    path('api/poll/<int:pk>/',PollDetail.as_view(),name='PollDetailAPIView')
]
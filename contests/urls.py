from django.urls import path
from .views import GetContestBySlugAPIView

urlpatterns = [
    path('contests/<slug:slug>/', GetContestBySlugAPIView.as_view(), name='get-contest'),
]

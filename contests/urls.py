from django.urls import path
from . import views
from .views import GetContestBySlugAPIView

urlpatterns = [
    path('contests/<slug:slug>/', GetContestBySlugAPIView.as_view(), name='get-contest'),
	path('fetch-s3-files/', views.fetch_s3_files, name='fetch_s3_files'),
]

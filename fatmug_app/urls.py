from django.urls import path
from .views import VideoUploadAPIView,SearchSubtitleView,OverallListVideoView

urlpatterns = [
    path('upload-video/', VideoUploadAPIView.as_view(), name='upload-video'),
    path('search-video/', SearchSubtitleView.as_view(), name='search-video'),
    path('list-video/', OverallListVideoView.as_view(), name='list-video')
]

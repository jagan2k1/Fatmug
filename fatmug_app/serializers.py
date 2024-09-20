from rest_framework import serializers
from .models import Video, Subtitle


class SubtitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subtitle
        fields = ['language', 'subtitle_file']


class VideoSerializer(serializers.ModelSerializer):
    subtitles = SubtitleSerializer(many=True, read_only=True)

    class Meta:
        model = Video
        fields = ['id', 'title', 'video_file', 'uploaded_at', 'subtitles']


class SearchSubtitleSerializer(serializers.Serializer):
    video_id = serializers.IntegerField()
    search_string = serializers.CharField()


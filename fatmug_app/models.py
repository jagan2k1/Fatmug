from django.db import models


class Video(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=255)
    video_file = models.FileField(upload_to='videos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)


class Subtitle(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='subtitles')
    language = models.CharField(max_length=50)  # Subtitle language, e.g., 'en', 'es'
    subtitle_file = models.FileField(upload_to='subtitles/')
    subtitle_json = models.TextField(blank=True, null=True)  # This field type is a guess.


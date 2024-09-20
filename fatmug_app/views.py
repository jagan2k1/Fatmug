import json
import subprocess
from django.core.files.base import ContentFile
from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from .models import Video, Subtitle
from .serializers import VideoSerializer, SearchSubtitleSerializer
from django.conf import settings
import os
import re


class VideoUploadAPIView(generics.GenericAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    parser_classes = [MultiPartParser]  # Add MultiPartParser for file uploads

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            video = serializer.save()
            self.process_video(video)  # This method processes the video
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def process_video(self, video):
    #     # Your video processing logic
    #     pass
    def parse_srt_file(self,file_path):
        # with open(file_path, 'r', encoding='utf-8') as file:
        data = file_path

        # Splitting the file by double newline to separate each block
        subtitle_blocks = data.strip().split('\n\n')

        # Regular expression to match timestamps
        timestamp_pattern = re.compile(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})')

        parsed_subtitles = []

        for block in subtitle_blocks:
            lines = block.split('\n')
            if len(lines) >= 3:
                # Extracting the index (first line), timestamp (second line), and subtitle (remaining lines)
                index = lines[0].strip()
                timestamp = lines[1].strip()
                subtitle_text = " ".join(lines[2:]).strip()

                # Matching the timestamp with regex
                match = timestamp_pattern.search(timestamp)
                if match:
                    start_time = match.group(1)
                    end_time = match.group(2)
                    parsed_subtitles.append({
                        'index': index,
                        'start_time': start_time,
                        'end_time': end_time,
                        'subtitle': subtitle_text
                    })

        return parsed_subtitles

    def process_video(self, video):
        video_path = video.video_file.path
        output_dir = os.path.join(settings.MEDIA_ROOT, 'subtitles')
        os.makedirs(output_dir, exist_ok=True)

        # Extract subtitles using ffmpeg (e.g., for English and Spanish subtitles)
        languages = ['en', 'es']
        for lang in languages:
            subtitle_output_path = os.path.join(output_dir, f'{video.id}_{lang}.srt')
            try:
                # Run ffmpeg to extract subtitles for specific language
                subprocess.run([
                    'ffmpeg', '-i', video_path, '-map', '0:s:0', '-c', 'srt',
                    '-scodec', 'copy', subtitle_output_path
                ], check=True)

                # Save subtitle to the database

                with open(subtitle_output_path, 'r') as subtitle_file:
                    subtitle_timeline_data = self.parse_srt_file(subtitle_file.read())
                    Subtitle.objects.create(
                        video=video,
                        language=lang,
                        subtitle_json = json.dumps(subtitle_timeline_data),
                        subtitle_file=ContentFile(subtitle_file.read(), f'{video.id}_{lang}.srt')
                    )
            except subprocess.CalledProcessError as e:
                print(f"Failed to extract subtitles for language {lang}: {e}")


class SearchSubtitleView(generics.GenericAPIView):
    queryset = Video.objects.all()
    serializer_class = SearchSubtitleSerializer

    def post(self, request, *args, **kwargs):
        try:
            subtitle_list = Subtitle.objects.filter(video=request.data["video_id"]).values()
            for subtitle_query in subtitle_list:
                data = []
                for subtitle in subtitle_query["subtitle_json"]:
                    if request.data["search_string"].lower() in subtitle['subtitle'].lower():
                        data.append({
                            "start_time": subtitle['start_time'],
                            "end_time": subtitle['end_time'],
                            "subtitile_string": subtitle['subtitle']
                        })
                if data:
                    return Response(data, status=status.HTTP_201_CREATED)
                else:
                    data = "No such subtitle occurs"
                    return Response(data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(e, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OverallListVideoView(generics.ListAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer

    def list(self, request, *args, **kwargs):
        try:
            data = []
            video_list = self.queryset.values()
            for video in video_list:
                subtitle_list = Subtitle.objects.filter(video = video["id"]).values()
                data.append(subtitle_list)
                # data.append({"subtitle":subtitle_list})

            return Response(data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(e, status=status.HTTP_500_INTERNAL_SERVER_ERROR)






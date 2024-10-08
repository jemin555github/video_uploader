from rest_framework import serializers
from core.models import Video, User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "password", "email"]


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ["id", "video_file"]

    def validate_video_file(self, value):
        if not value:
            raise serializers.ValidationError("Video file must be provided.")

        if not value.name.endswith((".mp4", ".avi", ".mov", ".mkv", ".wmv", "webm")):
            raise serializers.ValidationError(
                "Only this formate ('.mp4', '.avi', '.mov', '.mkv', '.wmv', 'webm') files are allowed."
            )

        return value

    def validate(self, attrs):
        if "video_file" not in attrs or not attrs["video_file"]:
            raise serializers.ValidationError(
                {"video_file": "Video file must be provided."}
            )
        return attrs

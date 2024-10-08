from django.shortcuts import render
from rest_framework.views import APIView
from core.serializers import VideoSerializer, RegisterSerializer
from core.models import Video
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status, views
from django.contrib.auth import authenticate
import os
from datetime import datetime
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication


# for register user first time
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User registered successfully."},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# provided token when user logged-in
class CustomLoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        # print(username, password)
        # Authenticate the user
        user = authenticate(username=username, password=password)
        if user is not None:
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            return Response(
                {"refresh": str(refresh), "access": str(refresh.access_token)},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"detail": "No active account found with the given credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )


# operations of video upload
class Video_process(APIView):
    permission_classes = [
        IsAuthenticated
    ]  # Only authenticated users can access this view
    # authentication_classes =  [BasicAuthentication]

    def post(self, request):
        video_file = request.FILES.get("video_file")
        if not video_file:
            return Response(
                {"detail": "No video file provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        title, _ = os.path.splitext(video_file.name)
        # print('title', title)
        video_serializer = VideoSerializer(data=request.data)

        if video_serializer.is_valid():
            video_serializer.save(
                title=title, created_by=request.user, is_deleted=False
            )
            return Response(video_serializer.data, status=status.HTTP_201_CREATED)

        return Response(video_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        video_id = request.query_params.get("id", None)
        filename = request.query_params.get("filename", None)
        if video_id is not None:
            try:
                video = Video.objects.get(
                    id=video_id, is_deleted=False, created_by=request.user
                )
                video_serializer = VideoSerializer(video)
                return Response(video_serializer.data, status=status.HTTP_200_OK)
            except Video.DoesNotExist:
                return Response(
                    {"detail": "Video not found."}, status=status.HTTP_404_NOT_FOUND
                )
        if filename:
            try:
                video = Video.objects.filter(
                    title__icontains=filename, is_deleted=False, created_by=request.user
                )

            except Video.DoesNotExist:
                return Response(
                    {"detail": "Video not found."}, status=status.HTTP_404_NOT_FOUND
                )

        # If no video_id is provided, return a list of all videos
        videos = Video.objects.filter(is_deleted=False, created_by=request.user)
        if videos:
            video_serializer = VideoSerializer(videos, many=True)
            return Response(video_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"detail": "Videos not found."}, status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request):
        video_id = request.data.get("id")

        if not video_id:
            return Response(
                {"detail": "Video ID is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            video = Video.objects.get(
                id=video_id, is_deleted=False, created_by=request.user
            )
        except Video.DoesNotExist:
            return Response(
                {"detail": "Video not found."}, status=status.HTTP_404_NOT_FOUND
            )

        video_serializer = VideoSerializer(video, data=request.data, partial=True)

        if video_serializer.is_valid():
            video_serializer.save(updated_by=request.user, updated_on=datetime.now())
            return Response(
                {"message": "Your data is edited", "data": video_serializer.data},
                status=status.HTTP_200_OK,
            )

        return Response(video_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        video_id = request.data.get("id")
        if not video_id:
            return Response(
                {"detail": "Video ID is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            video = Video.objects.get(
                id=video_id, is_deleted=False, created_by=request.user
            )
            video.is_deleted = True  # Mark as deleted instead of actually deleting
            video.save()

            return Response(
                {"detail": "Video deleted successfully."},
                status=status.HTTP_204_NO_CONTENT,
            )
        except Video.DoesNotExist:
            return Response(
                {"detail": "Video not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

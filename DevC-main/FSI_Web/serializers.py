from rest_framework import serializers
from .models import Post, Comments,Project, FSI_user

from rest_framework_jwt.settings import api_settings
from django.contrib.auth.models import User

class GetPostSerialize(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = '__all__'

class GetCommentsSerialize(serializers.ModelSerializer):

    class Meta:
        model = Comments
        fields = '__all__'


class GetAllProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = FSI_user
        fields = '__all__'

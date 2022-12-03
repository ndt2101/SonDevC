from django.shortcuts import render
from rest_framework import viewsets          # add this
from .serializers import PostSerializer      # add this
from .models import Post

# Create your views here.
class PostView(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    queryset = Post.objects.all()

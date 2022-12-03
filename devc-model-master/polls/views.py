from django.shortcuts import render
from rest_framework.decorators import api_view
from django.http.response import JsonResponse
from rest_framework import permissions, status
from rest_framework.parsers import JSONParser

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets
from django.db.models import Sum
from django.db.models import Subquery

import requests

from .models import Post, Comments, Project

from rq import Queue
from worker import conn

from dataCollector import getUserPage, collectData, getPageNames, getLongTermUserToken
from model import getReviewPredictList

q = Queue(connection=conn, default_timeout=3600)

# Create your views here.
def index(request):
    return JsonResponse({'message': 1}, status=status.HTTP_200_OK)

@api_view(['POST'])
def user_longterm_token(request):
    user_data = JSONParser().parse(request)
    if 'access_token' not in user_data:
        return JsonResponse({ 'message': 'Missing token' }, status=status.HTTP_400_BAD_REQUEST)

    try: 
        longterm_access_token = getLongTermUserToken(user_data['access_token'])
        print(longterm_access_token)
    except:
        return JsonResponse({ 'message': 'error' }, status=status.HTTP_400_BAD_REQUEST)

    return JsonResponse({'access_token': longterm_access_token}, status=status.HTTP_200_OK)

@api_view(['POST'])
def get_pages(request):
    user_data = JSONParser().parse(request)
    if 'access_token' not in user_data or 'user_id' not in user_data:
        return JsonResponse({ 'message': 'Missing fields' }, status=status.HTTP_400_BAD_REQUEST)

    try: 
        pages = getPageNames(user_data['access_token'], user_data['user_id'])
        print(pages)
    except:
        return JsonResponse({ 'message': 'error' }, status=status.HTTP_400_BAD_REQUEST)

    return JsonResponse({'pages': pages}, status=status.HTTP_200_OK)    

@api_view(['POST'])
def collect_comment_pages(request):
    user_data = JSONParser().parse(request)
    if 'access_token' not in user_data or 'page_id' not in user_data or 'keywords' not in user_data or 'last_collect_time' not in user_data or 'project_id' not in user_data:
        return JsonResponse({ 'message': 'Missing fields' }, status=status.HTTP_400_BAD_REQUEST)

    user_access_token = user_data['access_token']
    page_id = user_data['page_id']
    keywords = user_data['keywords']
    last_collect_time = user_data['last_collect_time']
    project_id = user_data['project_id']

    try:
        page_id, page_access_token, keywords = getUserPage(user_access_token, page_id, keywords)
        # commentRows, likeRows, collectTime = q.enqueue(collectData(page_id,page_access_token, keywords, last_collect_time))
        # data = q.enqueue(collectData(page_id,page_access_token, keywords, last_collect_time))
        q.enqueue(save_collected_comments, project_id, page_id,page_access_token, keywords, last_collect_time)
    except:
        return JsonResponse({ 'messasge': 'error' }, status=status.HTTP_400_BAD_REQUEST)
    return JsonResponse({'data': 'currently collecting data'}, status=status.HTTP_200_OK)

@api_view(['POST'])
def get_predictions(request):
    user_data = JSONParser().parse(request)
    if 'comments' not in user_data:
        return JsonResponse({ 'message': 'Missing fields' }, status=status.HTTP_400_BAD_REQUEST)

    comments = user_data['comments']
    predictions = getReviewPredictList(comments)
    return JsonResponse({'data': predictions}, status=status.HTTP_200_OK)

def save_collected_comments(project_id, page_id, page_access_token, keywords, last_collect_time):
    commentRows, likeRows, collectTime = collectData(page_id,page_access_token, keywords, last_collect_time)

    print('Saving comments...')
    for cmt in commentRows:
        requests.post('https://gentle-island-41460.herokuapp.com/postcmt/', json={
            "id": cmt['CommentID'],
            "post_id": cmt['PostID'],
            "content": cmt["Comment"],
            "num_likes": cmt['Likes'],
            "effect": "-1"
        })
    print('Done saving comments.')

    print('Saving likes...')
    for like in likeRows:
        requests.put('https://gentle-island-41460.herokuapp.com/putpost/{0}'.format(like["PostID"]), json={
            "id": like["PostID"],
            "project_id": project_id,
            "num_likes": like['Likes'],
            "num_comments": like['CommentNumber'],
            "content": like['Content']
        })
    print('Done saving likes.')

    print('Saving project...')
    requests.put('https://gentle-island-41460.herokuapp.com/putproject/{0}'.format(project_id), json={
        "lastCollectTime": collectTime
    })
    print('Done saving project.')

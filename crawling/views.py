from django.shortcuts import render
from crawling.service.crawling import search_img
# Create your views here.

def search_img2(request,word):
    url = search_img(word)
    print(url)
    return {'result': url}



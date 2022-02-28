# 네이버 검색 Open API 예제 - 이미지 검색
import os
import sys
import json
import urllib.parse  #  한글 -> 코드 자동 변환 프로그램
import urllib.request
import random

def search_img(word):
    client_id = "Sk76Td6MeuOwndj0QoSY"
    client_secret = "GRSC4DQ2c7"
    encText = urllib.parse.quote(word)
    url = "https://openapi.naver.com/v1/search/image?query=" + encText # json 결과
    # url = "https://openapi.naver.com/v1/search/blog.xml?query=" + encText # xml 결과
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id",client_id)
    request.add_header("X-Naver-Client-Secret",client_secret)
    response = urllib.request.urlopen(request)
    rescode = response.getcode()
    if(rescode==200):
        response_body = response.read()
        crawling_num = random.randrange(0,10)
        imgurl = json.loads(response_body.decode('utf-8'))['items'][crawling_num]['link']
        return imgurl
    else:
        print("Error Code:" + rescode)






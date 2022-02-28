from django.urls import path
from .views import search_img2

urlpatterns = [
    path('crwaling/<str:word>', search_img2),

]

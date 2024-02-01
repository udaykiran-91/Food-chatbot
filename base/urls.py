from django.urls import path
from . import chatbot,views

urlpatterns = [
    path("",chatbot.handle_request,name="handle"),
    path("home",views.home,name="home")
]

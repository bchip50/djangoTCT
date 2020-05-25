from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View, TemplateView
from django.core.exceptions import PermissionDenied
from datetime import datetime
from . import models

# Create your views here.
class HomeView(TemplateView):
    template_name = 'home.html'



from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.views import generic

from main.models import Mosaic


class MosaicView(generic.DetailView):
    model = Mosaic


def detail(request, id):
    return HttpResponse("hello")

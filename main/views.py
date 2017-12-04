from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseNotFound
from django.shortcuts import render

# Create your views here.
from main.models import Tags, Mosaic, MosaicPicture


def tags(request):
    print("in")
    tags_list = Tags.objects.all()
    for tag in tags_list:
        print (tag.tags)
    tags = [tag.tags for tag in tags_list]
    d = {
        'tags': tags_list
    }
    return render(request, "tags.html", d)


def tagPage(request, tagid):
    try:
        tag = Tags.objects.get(id=tagid)
    except ObjectDoesNotExist:
        return HttpResponseNotFound('<h1>Page not found</h1>')

    mosaics = Mosaic.objects.filter(tags=tag)
    mosaic_pics = MosaicPicture.objects.filter(mosaic__tags = tag)
    if len(mosaics) == 0:
        return HttpResponseNotFound('<h1>No Mosaics with this tag</h1>')

    d = {
        'mosaics': mosaics,
        'mosaic_pics': mosaic_pics
    }

    return render(request, "tagPage.html", d)
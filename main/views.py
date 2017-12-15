import folium as folium
from folium.plugins import MarkerCluster
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseNotFound
from django.shortcuts import render

# Create your views here.
from main.models import Tags, Mosaic, MosaicPicture
from django.views import generic


def tags(request):
    print("in")
    tags_list = Tags.objects.all()
    for tag in tags_list:
        print (tag.tag)
    tags = [tag.tag for tag in tags_list]
    d = {
        'tags': tags_list
    }
    return render(request, "tags.html", d)

class MosaicView(generic.DetailView):
    model = Mosaic

def tagPage(request, tagid):
    try:
        tag = Tags.objects.get(id=tagid)
    except ObjectDoesNotExist:
        return HttpResponseNotFound('<h1>Page not found</h1>')

    mosaics = set(Mosaic.objects.filter(tags=tag))
    # mosaic_pics = MosaicPicture.objects.filter(mosaic__tags = tag)
    mosaic_pics = []
    if len(mosaics) == 0:
        return HttpResponseNotFound('<h1>No Mosaics with this tag</h1>')

    for mosaic in mosaics:
        pictures = MosaicPicture.objects.filter(mosaic=mosaic).order_by('order_priority')
        mosaic_pics.append(pictures[0])

    d = {
        'mosaics': mosaics,
        'mosaic_pics': mosaic_pics
    }

    return render(request, "tagPage.html", d)

def map(request):
    mosaics = Mosaic.objects.all()
    map = folium.Map(
        location=[31.781959, 35.2137],
        tiles='Stamen Toner',
        zoom_start=12
    )
    marker_cluster = MarkerCluster().add_to(map)
    for point in mosaics:
        folium.Marker(
            location = [point.dimen_width, point.dimen_length],
            popup = point.title
        ).add_to(marker_cluster)
    map.save("main/templates/map.html")

    return render(request, "MapPage.html")

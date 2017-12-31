import folium
from django.views.generic import TemplateView, DetailView, ListView
from folium.plugins import MarkerCluster
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseNotFound
from django.shortcuts import render
from main.models import Tag, MosaicItem, MosaicPicture, MosaicSite
from django.utils.translation import ugettext as _

from mosaic_prj.base_views import IAAUIMixin


class HomeView(IAAUIMixin, TemplateView):
    template_name = 'main/home.html'
    page_title = _('Home page')
    page_name = 'home'


class MosaicView(DetailView):
    model = MosaicItem
    template_name = 'main/mosaic_detail.html'
    context_object_name = 'mosaic'


def tags(request):
    print("in")
    tags_list = Tag.objects.all()
    for tag in tags_list:
        print(tag.tag)
    tags = [tag.tag for tag in tags_list]
    d = {
        'tags': tags_list
    }
    return render(request, "tags.html", d)


def tag_page(request, tagid):
    try:
        tag = Tag.objects.get(id=tagid)
    except ObjectDoesNotExist:
        return HttpResponseNotFound('<h1>Page not found</h1>')

    mosaics = set(MosaicItem.objects.filter(tags=tag))
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

    return render(request, "tag_page.html", d)


def mosaic_map(request):
    mosaics = MosaicItem.objects.all()
    m = folium.Map(
        location=[31.781959, 35.2137],
        tiles='Stamen Toner',
        zoom_start=12
    )
    marker_cluster = MarkerCluster().add_to(m)
    for point in mosaics:
        folium.Marker(
            location=[point.dimen_width, point.dimen_length],
            popup=point.title
        ).add_to(marker_cluster)
    m.save("main/templates/map.html")

    return render(request, "map_page.html")


class SiteListView(ListView):
    model = MosaicSite
    template_name = 'main/site_list.html'
    context_object_name = 'site_list'


    def get_queryset(self):
        return MosaicSite.objects.order_by('-title').reverse()

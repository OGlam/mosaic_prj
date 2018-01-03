import folium
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils import translation
from django.views.generic import TemplateView, DetailView, ListView, CreateView, UpdateView, DeleteView
from folium.plugins import MarkerCluster
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseNotFound
from django.shortcuts import render
from django.utils.translation import ugettext as _

from .forms import TagForm, MosaicSiteForm, MosaicItemForm, MosaicItemUpdateForm, MosaicPictureFormSet
from .models import Tag, MosaicItem, MosaicPicture, MosaicSite, ArchaeologicalContext

from mosaic_prj.base_views import IAAUIMixin


class HomeView(IAAUIMixin, TemplateView):
    template_name = 'main/home.html'
    page_title = _('Home page')
    page_name = 'home'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        mosaic_items = MosaicItem.objects.filter(mosaic_site__featured=True)
        context['popular_sites'] = mosaic_items[:3]
        context['popular_sites_sub'] = mosaic_items[3:5]
        context['tags'] = MosaicPicture.objects.filter(tags__isnull=False).distinct('tags__tag_he')
        context['archeological_context'] = [
            MosaicPicture.objects.filter(mosaic__mosaic_site__archaeological_context=x).first() for x in
            ArchaeologicalContext.CHOICES
        ]
        # context['map_context'] = self.getMapDataContext()
        return context

    def getMapDataContext(self):
        pass


class MosaicView(DetailView):
    model = MosaicItem
    template_name = 'main/mosaic_detail.html'
    context_object_name = 'mosaic'


class TagCreateView(IAAUIMixin, CreateView):
    template_name = 'main/tag_form.html'
    model = Tag
    form_class = TagForm
    success_url = reverse_lazy('main:tag_create')
    page_title = _('Tag create')
    page_name = 'tag_create'

    def get_context_data(self, **kwargs):
        d = super(TagCreateView, self).get_context_data(**kwargs)
        d['tags'] = Tag.objects.all()
        return d


class TagUpdateView(IAAUIMixin, UpdateView):
    template_name = 'main/tag_form.html'
    model = Tag
    form_class = TagForm
    success_url = reverse_lazy('main:tag_create')
    page_title = _('Tag update')
    page_name = 'tag_update'


class TagDeleteView(IAAUIMixin, DeleteView):
    model = Tag
    success_url = reverse_lazy('main:tag_create')


class MosaicSiteCreateView(SuccessMessageMixin, IAAUIMixin, CreateView):
    template_name = 'main/mosaic_site_form.html'
    model = MosaicSite
    form_class = MosaicSiteForm
    success_url = reverse_lazy('main:site_create')
    success_message = _('Mosaic site created successfully')
    page_title = _('Mosaic site create')
    page_name = 'mosaic_site_create'

    def get_context_data(self, **kwargs):
        d = super(MosaicSiteCreateView, self).get_context_data(**kwargs)
        d['sites'] = MosaicSite.objects.all()
        return d


class MosaicSiteUpdateView(SuccessMessageMixin, IAAUIMixin, UpdateView):
    template_name = 'main/mosaic_site_form.html'
    model = MosaicSite
    form_class = MosaicSiteForm
    success_url = reverse_lazy('main:site_create')
    success_message = _('Mosaic site updated successfully')
    page_title = _('Mosaic site update')
    page_name = 'mosaic_site_update'


class MosaicSiteDeleteView(IAAUIMixin, DeleteView):
    model = MosaicSite
    success_url = reverse_lazy('main:site_create')


class MosaicItemListView(IAAUIMixin, ListView):
    model = MosaicItem
    template_name = 'main/mosaic_item_list.html'
    context_object_name = 'items'


class MosaicItemCreateView(SuccessMessageMixin, IAAUIMixin, CreateView):
    template_name = 'main/mosaic_item_form.html'
    model = MosaicItem
    form_class = MosaicItemForm
    success_message = _('Mosaic item created successfully')
    page_title = _('Mosaic item create')
    page_name = 'mosaic_sitem_create'

    def get_success_url(self):
        return reverse_lazy('main:item_list')

    def form_valid(self, form):
        context = self.get_context_data()
        mosaic_picture_formset = context['mosaic_picture_formset']

        if mosaic_picture_formset.is_valid():
            self.object = form.save()
            mosaic_picture_formset.instance = self.object
            mosaic_picture_formset.save()
            return super().form_valid(form)

        return self.render_to_response(
            self.get_context_data(
                form=form,
                mosaic_picture_formset=mosaic_picture_formset
            )
        )
        # return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        d = super(MosaicItemCreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            d['mosaic_picture_formset'] = MosaicPictureFormSet(self.request.POST, self.request.FILES,
                                                               prefix='mosaic_picture_formset')
        else:
            d['mosaic_picture_formset'] = MosaicPictureFormSet(prefix='mosaic_picture_formset')
        return d


class MosaicItemUpdateView(SuccessMessageMixin, IAAUIMixin, UpdateView):
    template_name = 'main/mosaic_item_form.html'
    model = MosaicItem
    form_class = MosaicItemUpdateForm
    success_message = _('Mosaic item updated successfully')
    page_title = _('Mosaic item update')
    page_name = 'mosaic_item_update'

    def get_initial(self):
        return {
            'materials': tuple(self.object.materials)
        }

    def get_success_url(self):
        return reverse_lazy('main:item_list')

    def form_valid(self, form):
        context = self.get_context_data()
        mosaic_picture_formset = context['mosaic_picture_formset']

        if mosaic_picture_formset.is_valid():
            self.object = form.save()
            mosaic_picture_formset.save()
            return super().form_valid(form)

        return self.render_to_response(
            self.get_context_data(
                form=form,
                mosaic_picture_formset=mosaic_picture_formset
            )
        )
        # return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        d = super(MosaicItemUpdateView, self).get_context_data(**kwargs)
        if self.request.POST:
            d['mosaic_picture_formset'] = MosaicPictureFormSet(
                self.request.POST,
                self.request.FILES,
                prefix='mosaic_picture_formset',
                instance=self.object
            )
        else:
            d['mosaic_picture_formset'] = MosaicPictureFormSet(
                prefix='mosaic_picture_formset',
                instance=self.object
            )
        return d


class MosaicItemDeleteView(SuccessMessageMixin, IAAUIMixin, DeleteView):
    model = MosaicItem
    success_message = _('Mosaic item deleted successfully')

    def get_success_url(self):
        return reverse_lazy('main:item_list')


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
        lang = translation.get_language()[:2]
        title = 'title_he' if lang == 'he' else 'title_en'
        return MosaicSite.objects.order_by(title)

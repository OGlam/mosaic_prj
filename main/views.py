import random
import re
from collections import OrderedDict

from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseNotFound
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView, DetailView, ListView, \
    CreateView, UpdateView, DeleteView, FormView

from mosaic_prj.base_views import IAAUIMixin
from .forms import TagForm, MosaicSiteForm, MosaicItemForm, \
    MosaicItemUpdateForm, MosaicPictureFormSet, AboutForm
from .models import Tag, MosaicItem, MosaicPicture, MosaicSite, \
    ArchaeologicalContext, GeneralSettings, HOME_BANNERS


class SiteView(IAAUIMixin, DetailView):
    template_name = 'main/mosaic_site.html'
    page_title = _('Mosaic Site')
    page_name = 'site'
    model = MosaicSite
    context_object_name = 'mosaic'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class HomeView(IAAUIMixin, TemplateView):
    template_name = 'main/home.html'
    page_title = _('Home page')
    page_name = 'home'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cover_pictures = MosaicPicture.objects.filter(is_cover=True).exclude(
            mosaic__mosaic_site__featured=False)
        mosaic_item_ids = [x.mosaic.id for x in cover_pictures]

        mosaic_items = MosaicItem.objects.filter(
            id__in=mosaic_item_ids).order_by('?')
        # mosaic_items = MosaicItem.objects.filter(id__in=mosaic_item_ids).order_by('mosaic_site')
        # context['popular_sites'] = mosaic_items[:3]
        context['popular_site'] = HOME_BANNERS[random.randint(0, 2)]
        context['popular_sites_sub'] = mosaic_items[:2]
        # context['popular_sites_sub'] = mosaic_items[3:5]
        tags = Tag.objects.filter(featured=True)
        # tag_pic_ids = []
        # for tag in tags:
        #     tag_pic_ids.extend(
        #         tag.mosaic_pictures.values_list('id', flat=True))
        # context['tags'] = MosaicPicture.objects.filter(
        #     id__in=tag_pic_ids).order_by('?')[:5]
        context['tags'] = tags.order_by('?')[:5]
        context['archaeological_context'] = [
            MosaicPicture.objects.filter(
                mosaic__mosaic_site__archaeological_context=x[0]).exclude(
                picture__isnull=True).first() for x in
            ArchaeologicalContext.CHOICES if
            MosaicPicture.objects.filter(
                mosaic__mosaic_site__archaeological_context=x[0]).exclude(
                picture__isnull=True).exists()
        ]
        lang = translation.get_language()[:2]
        context['map_lang'] = 'iw' if lang == 'he' else 'en'
        context['map_markers'] = [
            [u'{}'.format(getattr(x, "title_" + lang)), x.latitude,
             x.longitude, x.id] for x in
            MosaicSite.objects.filter(latitude__isnull=False,
                                      longitude__isnull=False)
        ]
        context['sites'] = MosaicSite.objects.filter(latitude__isnull=False,
                                                     longitude__isnull=False)
        return context


class AboutView(IAAUIMixin, TemplateView):
    template_name = 'main/about.html'
    page_title = _('About page')
    page_name = 'about'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        general_settings = GeneralSettings.get_solo()
        lang = translation.get_language()[:2]
        context['content'] = getattr(general_settings, "about_" + lang)
        return context


class AboutEditView(IAAUIMixin, FormView):
    template_name = 'main/about_form.html'
    form_class = AboutForm
    success_url = reverse_lazy('about_edit')
    page_title = _('About edit page')
    page_name = 'about_edit'

    def get_initial(self):
        general_settings = GeneralSettings.get_solo()
        return {
            'content_he': general_settings.about_he,
            'content_en': general_settings.about_en
        }

    def form_valid(self, form):
        obj = GeneralSettings.get_solo()
        obj.about_he = form.cleaned_data['content_he']
        obj.about_en = form.cleaned_data['content_en']
        obj.save()
        return super().form_valid(form)


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
    page_name = 'items'
    page_title = 'Items'
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

        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        d = super(MosaicItemCreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            d['mosaic_picture_formset'] = MosaicPictureFormSet(
                self.request.POST, self.request.FILES,
                prefix='mosaic_picture_formset')
        else:
            d['mosaic_picture_formset'] = MosaicPictureFormSet(
                prefix='mosaic_picture_formset')
        return d


class MosaicItemUpdateView(SuccessMessageMixin, IAAUIMixin, UpdateView):
    template_name = 'main/mosaic_item_form.html'
    model = MosaicItem
    form_class = MosaicItemUpdateForm
    success_message = _('Mosaic item updated successfully')
    page_title = _('Mosaic item update')
    page_name = 'mosaic_item_update'

    def get_initial(self):
        d = {}

        if self.object.materials:
            d['materials'] = tuple(self.object.materials)

        return d

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
        pictures = MosaicPicture.objects.filter(mosaic=mosaic).order_by(
            'order_priority')
        mosaic_pics.append(pictures[0])

    d = {
        'mosaics': mosaics,
        'mosaic_pics': mosaic_pics
    }

    return render(request, "tag_page.html", d)


class SiteListView(IAAUIMixin, ListView):
    model = MosaicSite
    template_name = 'main/site_list.html'
    context_object_name = 'site_list'
    page_name = 'sites'
    page_title = 'Sites'

    def get_queryset(self):
        lang = translation.get_language()[:2]
        title = 'title_he' if lang == 'he' else 'title_en'
        return MosaicSite.objects.order_by(title)

    def get_context_data(self, **kwargs):
        d = super().get_context_data(**kwargs)
        lang = translation.get_language()[:2]
        if lang == 'he':
            am_l = [x.id for x in self.get_queryset() if
                    re.match('[אבגדהוזחטיכלמ]', x.title_he[0])]
            d['am_list'] = self.get_queryset().filter(id__in=am_l)
            nz_l = [x.id for x in self.get_queryset() if
                    re.match('[נסעפצקרשת]', x.title_he[0])]
            d['nz_list'] = self.get_queryset().filter(id__in=nz_l)
        else:
            am_l = [x.id for x in self.get_queryset() if
                    re.match('[a-mA-M]', x.title_en[0])]
            d['am_list'] = self.get_queryset().filter(id__in=am_l)
            nz_l = [x.id for x in self.get_queryset() if
                    re.match('[n-zN-Z]', x.title_en[0])]
            d['nz_list'] = self.get_queryset().filter(id__in=nz_l)
        # am_l = [x.id for x in self.get_queryset() if re.match('[אבגדהוזחטיכלמ]', x.title_he) or re.match('[a-mA-M]', x.title_en)]
        # d['am_list'] = self.get_queryset().filter(id__in=am_l)
        # nz_l = [x.id for x in self.get_queryset() if re.match('[נסעפצקרשת]', x.title_he) or re.match('[n-zN-Z]', x.title_en)]
        # d['nz_list'] = self.get_queryset().filter(id__in=nz_l)
        return d


class SubjectsView(IAAUIMixin, ListView):
    model = Tag
    template_name = 'main/subjects.html'
    page_name = 'subjects'
    page_title = _('Subjects')

    def get_queryset(self):
        lang = translation.get_language()[:2]
        order_by = 'tag_he' if lang == 'he' else 'tag_en'
        return super().get_queryset().order_by(order_by).exclude(mosaic_items=None)

    def get_context_data(self, **kwargs):
        d = super().get_context_data(**kwargs)
        return d


class PeriodsView(IAAUIMixin, ListView):
    model = MosaicSite
    template_name = 'main/periods.html'
    context_object_name = 'sites'
    page_name = 'periods'
    page_title = _('Periods')

    def get_queryset(self):
        return super().get_queryset().order_by('period')

    def get_context_data(self, **kwargs):
        d = super().get_context_data(**kwargs)
        return d


class SubjectView(IAAUIMixin, ListView):
    model = MosaicItem
    template_name = 'main/subject.html'
    page_name = 'subject'
    page_title = _('Subject')

    def get_queryset(self):
        return super().get_queryset().filter(tags=int(self.kwargs['tag_id']))

    def get_context_data(self, **kwargs):
        d = super().get_context_data(**kwargs)
        d['tag'] = Tag.objects.get(pk=int(self.kwargs['tag_id']))
        return d

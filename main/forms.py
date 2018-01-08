from django import forms
from django.forms import inlineformset_factory

from .models import Tag, MosaicSite, ArchaeologicalContext, MosaicItem, Materials, MosaicPicture, PictureType


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = '__all__'
        widgets = {
            'tag_he': forms.TextInput(attrs={'class': 'form-control', 'dir': 'rtl'}),
            'tag_en': forms.TextInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
        }

    def __init__(self, *args, **kwargs):
        super(TagForm, self).__init__(*args, **kwargs)
        if self.errors:
            for field in self.fields:
                if field in self.errors:
                    classes = self.fields[field].widget.attrs.get('class', '')
                    classes += ' is-invalid'
                    self.fields[field].widget.attrs['class'] = classes


class MosaicSiteForm(forms.ModelForm):
    class Meta:
        model = MosaicSite
        exclude = [
            'created_at'
        ]
        widgets = {
            'site_id': forms.TextInput(attrs={'class': 'form-control'}),
            'title_he': forms.TextInput(attrs={'class': 'form-control', 'dir': 'rtl'}),
            'title_en': forms.TextInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'origin_he': forms.TextInput(attrs={'class': 'form-control', 'dir': 'rtl'}),
            'origin_en': forms.TextInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'story_he': forms.Textarea(attrs={'class': 'form-control', 'dir': 'rtl'}),
            'story_en': forms.Textarea(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'archaeological_context': forms.Select(attrs={'class': 'form-control'},
                                                   choices=ArchaeologicalContext.CHOICES),
            'period': forms.TextInput(attrs={'class': 'form-control'}),
            'video_id': forms.TextInput(attrs={'class': 'form-control'}),
            'comments': forms.TextInput(attrs={'class': 'form-control'}),
            'featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'latitude': forms.TextInput(attrs={'class': 'form-control'}),
            'longitude': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(MosaicSiteForm, self).__init__(*args, **kwargs)
        if self.errors:
            for field in self.fields:
                if field in self.errors:
                    classes = self.fields[field].widget.attrs.get('class', '')
                    classes += ' is-invalid'
                    self.fields[field].widget.attrs['class'] = classes


class MosaicItemForm(forms.ModelForm):
    class Meta:
        model = MosaicItem
        exclude = [
            'created_at',
        ]
        widgets = {
            'mosaic_site': forms.Select(attrs={'class': 'form-control'}),
            'misp_rashut': forms.TextInput(attrs={'class': 'form-control'}),
            'description_he': forms.Textarea(attrs={'class': 'form-control', 'dir': 'rtl'}),
            'description_en': forms.Textarea(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'length': forms.TextInput(attrs={'class': 'form-control'}),
            'width': forms.TextInput(attrs={'class': 'form-control'}),
            'area': forms.TextInput(attrs={'class': 'form-control'}),
            'rishayon': forms.TextInput(attrs={'class': 'form-control'}),
            'materials': forms.SelectMultiple(attrs={'class': 'form-control'},
                                              choices=Materials.CHOICES),
            'year': forms.TextInput(attrs={'class': 'form-control'}),
            'displayed_at': forms.TextInput(attrs={'class': 'form-control'}),
            'bibliography_he': forms.Textarea(attrs={'class': 'form-control', 'dir': 'rtl'}),
            'bibliography_en': forms.Textarea(attrs={'class': 'form-control', 'dir': 'ltr'}),
        }

    def __init__(self, *args, **kwargs):
        super(MosaicItemForm, self).__init__(*args, **kwargs)
        if self.errors:
            for field in self.fields:
                if field in self.errors:
                    classes = self.fields[field].widget.attrs.get('class', '')
                    classes += ' is-invalid'
                    self.fields[field].widget.attrs['class'] = classes


class MosaicItemUpdateForm(MosaicItemForm):
    class Meta(MosaicItemForm.Meta):
        exclude = MosaicItemForm.Meta.exclude + ['mosaic_site']


class MosaicPictureForm(forms.ModelForm):
    class Meta:
        model = MosaicPicture
        fields = [
            'picture',
            'negative_id',
            'photographer_name_he',
            'photographer_name_en',
            'taken_at',
            'picture_type',
            'taken_date',
            'comments_he',
            'comments_en',
            'tags',
            'order_priority',
            'is_cover',
        ]
        widgets = {
            'picture': forms.FileInput(attrs={'class': 'form-control-file'}),
            'negative_id': forms.TextInput(attrs={'class': 'form-control'}),
            'photographer_name_he': forms.TextInput(attrs={'class': 'form-control', 'dir': 'rtl'}),
            'photographer_name_en': forms.TextInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'taken_at': forms.TextInput(attrs={'class': 'form-control'}),
            'picture_type': forms.Select(attrs={'class': 'form-control'}, choices=PictureType.CHOICES),
            'taken_date': forms.DateInput(attrs={'class': 'form-control'}),
            'comments_he': forms.Textarea(attrs={'class': 'form-control', 'dir': 'rtl'}),
            'comments_en': forms.Textarea(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'order_priority': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_cover': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super(MosaicPictureForm, self).__init__(*args, **kwargs)
        if self.errors:
            for field in self.fields:
                if field in self.errors:
                    classes = self.fields[field].widget.attrs.get('class', '')
                    classes += ' is-invalid'
                    self.fields[field].widget.attrs['class'] = classes


MosaicPictureFormSet = inlineformset_factory(
    MosaicItem,
    MosaicPicture,
    form=MosaicPictureForm,
    extra=2,
    can_delete=False
)

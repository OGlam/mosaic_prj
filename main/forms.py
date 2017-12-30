from django import forms

from .models import Tag, MosaicSite, ArcheologicalContext, MosaicItem, Materials


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = '__all__'
        widgets = {
            'tag_he': forms.TextInput(attrs={'class': 'form-control'}),
            'tag_en': forms.TextInput(attrs={'class': 'form-control'}),
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
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'origin': forms.TextInput(attrs={'class': 'form-control'}),
            'story': forms.Textarea(attrs={'class': 'form-control'}),
            'archeological_context': forms.Select(attrs={'class': 'form-control'},
                                                  choices=ArcheologicalContext.CHOICES),
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
            'mosaic_site'
        ]
        widgets = {
            'misp_rashut': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'length': forms.TextInput(attrs={'class': 'form-control'}),
            'width': forms.TextInput(attrs={'class': 'form-control'}),
            'area': forms.TextInput(attrs={'class': 'form-control'}),
            'rishayon': forms.TextInput(attrs={'class': 'form-control'}),
            'materials': forms.SelectMultiple(attrs={'class': 'form-control'},
                                              choices=Materials.CHOICES),
            'year': forms.TextInput(attrs={'class': 'form-control'}),
            'displayed_at': forms.TextInput(attrs={'class': 'form-control'}),
            'bibliography': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(MosaicItemForm, self).__init__(*args, **kwargs)
        if self.errors:
            for field in self.fields:
                if field in self.errors:
                    classes = self.fields[field].widget.attrs.get('class', '')
                    classes += ' is-invalid'
                    self.fields[field].widget.attrs['class'] = classes

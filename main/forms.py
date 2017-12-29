from django import forms

from .models import Tag


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = '__all__'
        widgets = {
            'tag_he': forms.TextInput(attrs={'class': 'form-control'}),
            'tag_en': forms.TextInput(attrs={'class': 'form-control'}),
        }

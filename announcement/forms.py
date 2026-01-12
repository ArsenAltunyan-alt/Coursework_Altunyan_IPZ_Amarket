from django import forms
from .models import Announcement

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'category', 'condition', 'description', 'price', 'is_negotiable', 'address']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Назва оголошення'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'condition': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Опис оголошення', 'rows': 5}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ціна (необов\'язково)'}),
            'is_negotiable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Адреса'}),
        }

class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True

class AnnouncementImageForm(forms.Form):
    images = forms.FileField(
        widget=MultipleFileInput(attrs={'multiple': True, 'class': 'form-control'}),
        label='Фотографії (максимум 10)',
        required=False
    )
    main_image_index = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=False,
        initial=0
    )

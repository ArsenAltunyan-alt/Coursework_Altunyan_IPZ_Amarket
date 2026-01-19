from django import forms
from .models import Announcement, Category

class AnnouncementForm(forms.ModelForm):
    category_parent = forms.ModelChoiceField(
        queryset=Category.objects.none(),
        required=True,
        label='Category',
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_category_parent'}),
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.none(),
        required=False,
        label='Subcategory',
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_category'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category_parent'].queryset = Category.objects.filter(parent__isnull=True).order_by('name')
        self.fields['category'].queryset = Category.objects.filter(parent__isnull=False).select_related('parent').order_by('parent__name', 'name')

        instance = kwargs.get('instance')
        if instance and instance.category_id:
            if instance.category.parent_id:
                self.initial['category_parent'] = instance.category.parent_id
                self.initial['category'] = instance.category_id
            else:
                self.initial['category_parent'] = instance.category_id
                self.initial['category'] = None

    def clean(self):
        cleaned_data = super().clean()
        category_parent = cleaned_data.get('category_parent')
        subcategory = cleaned_data.get('category')

        if subcategory and category_parent and subcategory.parent_id != category_parent.id:
            self.add_error('category', 'Selected subcategory does not belong to selected category.')

        if not subcategory:
            cleaned_data['category'] = category_parent

        return cleaned_data

    class Meta:
        model = Announcement
        fields = ['title', 'category', 'condition', 'description', 'price', 'is_negotiable', 'address', 'latitude', 'longitude']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Назва оголошення'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'condition': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Опис оголошення', 'rows': 5}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ціна (необов\'язково)'}),
            'is_negotiable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Адреса', 'id': 'address-input'}),
            'latitude': forms.HiddenInput(attrs={'id': 'id_latitude'}),
            'longitude': forms.HiddenInput(attrs={'id': 'id_longitude'}),
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

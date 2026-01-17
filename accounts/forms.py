from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser


class RegistrationStep1Form(UserCreationForm):
    """Форма для першого кроку реєстрації - основна інформація"""
    
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Введіть ваше ім\'я'
        }),
        label="Ім'я"
    )
    
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Введіть ваше прізвище'
        }),
        label="Прізвище"
    )
    
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'example@email.com'
        }),
        label="Email"
    )
    
    phone_number = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '+380XXXXXXXXX'
        }),
        label="Номер телефону"
    )
    
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Оберіть логін'
            }),
        }
        labels = {
            'username': 'Логін',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Введіть пароль'
        })
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Підтвердіть пароль'
        })
        self.fields['password2'].label = 'Підтвердження пароля'
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if CustomUser.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError('Користувач з таким номером телефону вже існує.')
        return phone_number
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('Користувач з таким email вже існує.')
        return email


class RegistrationStep2Form(forms.ModelForm):
    """Форма для другого кроку реєстрації - вибір міста"""
    
    class Meta:
        model = CustomUser
        fields = ['city']
        widgets = {
            'city': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Введіть ваше місто'
            }),
        }
        labels = {
            'city': 'Місто',
        }


class RegistrationStep3Form(forms.ModelForm):
    """Форма для третього кроку реєстрації - завантаження фото"""
    
    class Meta:
        model = CustomUser
        fields = ['profile_photo']
        widgets = {
            'profile_photo': forms.FileInput(attrs={
                'class': 'form-input',
                'accept': 'image/*'
            }),
        }
        labels = {
            'profile_photo': 'Фото профілю',
        }


class CustomLoginForm(AuthenticationForm):
    """Кастомна форма входу"""
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Логін'
        }),
        label='Логін'
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Пароль'
        }),
        label='Пароль'
    )


class ProfileUpdateForm(forms.ModelForm):
    """Форма для редагування профілю"""
    
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'city', 'profile_photo']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ім\'я'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Прізвище'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'Email'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Номер телефону'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Місто'
            }),
            'profile_photo': forms.FileInput(attrs={
                'class': 'form-input',
                'accept': 'image/*'
            }),
        }
        labels = {
            'first_name': 'Ім\'я',
            'last_name': 'Прізвище',
            'email': 'Email',
            'phone_number': 'Номер телефону',
            'city': 'Місто',
            'profile_photo': 'Фото профілю',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].required = False

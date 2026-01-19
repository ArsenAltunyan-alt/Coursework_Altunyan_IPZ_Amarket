from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from allauth.socialaccount.models import SocialAccount
from .forms import (
    RegistrationStep1Form,
    RegistrationStep2Form,
    RegistrationStep3Form,
    CustomLoginForm,
    ProfileUpdateForm,
    CustomPasswordChangeForm,
    AccountDeleteForm
)
from .models import CustomUser


def register_step1(request):
    if request.user.is_authenticated:
        return redirect('accounts:profile')
    
    if request.method == 'POST':
        form = RegistrationStep1Form(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, 'Основну інформацію збережено! Перейдіть до наступного кроку.')
            return redirect('accounts:register_step2')
    else:
        request.session['social_login_action'] = 'signup'
        
        initial_data = {}
        if request.session.get('google_signup'):
            initial_data['email'] = request.session.get('google_email', '')
            initial_data['first_name'] = request.session.get('google_first_name', '')
            initial_data['last_name'] = request.session.get('google_last_name', '')
            
        form = RegistrationStep1Form(initial=initial_data)
    
    return render(request, 'accounts/register_step1.html', {
        'form': form,
        'current_step': 1,
        'total_steps': 3
    })


@login_required
def register_step2(request):
    """Другий крок реєстрації вибір міста"""
    if request.method == 'POST':
        if 'skip' in request.POST:
            messages.info(request, 'Ви пропустили вибір міста.')
            return redirect('accounts:register_step3')
        
        form = RegistrationStep2Form(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Місто збережено!')
            return redirect('accounts:register_step3')
    else:
        form = RegistrationStep2Form(instance=request.user)
    
    return render(request, 'accounts/register_step2.html', {
        'form': form,
        'current_step': 2,
        'total_steps': 3
    })


@login_required
def register_step3(request):
    """Третій крок реєстрації завантаження фото"""
    if request.method == 'POST':
        if 'skip' in request.POST:
            messages.info(request, 'Ви пропустили завантаження фото.')
            return redirect('accounts:profile')
        
        form = RegistrationStep3Form(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Реєстрацію завершено! Ласкаво просимо!')
            return redirect('accounts:profile')
    else:
        form = RegistrationStep3Form(instance=request.user)
    
    return render(request, 'accounts/register_step3.html', {
        'form': form,
        'current_step': 3,
        'total_steps': 3
    })


def user_login(request):
    if request.user.is_authenticated:
        return redirect('accounts:profile')
    
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, f'Ласкаво просимо, {user.first_name} {user.last_name}!')
                return redirect('accounts:profile')
    else:
        request.session['social_login_action'] = 'login'
        form = CustomLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def user_logout(request):
    logout(request)
    messages.info(request, 'Ви успішно вийшли з системи.')
    return redirect('accounts:login')


@login_required
def profile(request):
    is_google_user = SocialAccount.objects.filter(user=request.user, provider='google').exists()
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профіль успішно оновлено!')
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    return render(request, 'accounts/profile.html', {
        'form': form,
        'user': request.user,
        'is_google_user': is_google_user
    })


@login_required
def post_login_redirect(request):
    user = request.user

    if not user.city:
        return redirect('accounts:register_step2')

    return redirect('accounts:profile')


@login_required
def password_change(request):
    is_google_user = SocialAccount.objects.filter(user=request.user, provider='google').exists()
    if is_google_user:
        messages.info(request, 'Password changes are not available for Google accounts.')
        return redirect('accounts:profile')

    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Password updated successfully.')
            return redirect('accounts:profile')
    else:
        form = CustomPasswordChangeForm(user=request.user)

    return render(request, 'accounts/password_change.html', {
        'form': form
    })


@login_required
def account_delete(request):
    if request.method == 'POST':
        form = AccountDeleteForm(request.POST, user=request.user)
        if form.is_valid():
            user = request.user
            logout(request)
            user.delete()
            messages.success(request, 'Your account has been deleted.')
            return redirect('accounts:login')
    else:
        form = AccountDeleteForm(user=request.user)

    return render(request, 'accounts/account_delete.html', {
        'form': form
    })


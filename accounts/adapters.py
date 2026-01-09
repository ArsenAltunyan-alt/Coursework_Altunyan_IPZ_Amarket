from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from django.shortcuts import redirect


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Кастомний адаптер для обробки OAuth аутентифікації"""
    
    def pre_social_login(self, request, sociallogin):
        """
        Викликається після успішної OAuth аутентифікації,
        але перед створенням/входом користувача
        """
        if sociallogin.is_existing:
            return
        
        if sociallogin.account.provider == 'google':
            email = sociallogin.account.extra_data.get('email', '')
            name = sociallogin.account.extra_data.get('name', '')
            given_name = sociallogin.account.extra_data.get('given_name', '')
            family_name = sociallogin.account.extra_data.get('family_name', '')
            
            if not given_name and name:
                parts = name.split(' ', 1)
                given_name = parts[0]
                if len(parts) > 1:
                    family_name = parts[1]
            
            action = request.session.get('social_login_action')
            
            if action == 'signup':
                return

            request.session['google_signup'] = True
            request.session['google_email'] = email
            request.session['google_first_name'] = given_name
            request.session['google_last_name'] = family_name
            request.session.save()
            
            raise ImmediateHttpResponse(redirect('accounts:register_step1'))
    
    def save_user(self, request, sociallogin, form=None):
        """
        Зберігає користувача після OAuth аутентифікації
        """
        user = super().save_user(request, sociallogin, form)
        
        if sociallogin.account.provider == 'google':
            extra_data = sociallogin.account.extra_data
            
            given_name = extra_data.get('given_name')
            family_name = extra_data.get('family_name')
            name = extra_data.get('name')

            if not given_name and name:
                parts = name.split(' ', 1)
                given_name = parts[0]
                if len(parts) > 1:
                    family_name = parts[1]

            if given_name and not user.first_name:
                user.first_name = given_name
            if family_name and not user.last_name:
                user.last_name = family_name
            
            if not user.phone_number:
                user.phone_number = None
            
            user.save()
        
        return user


class CustomAccountAdapter(DefaultAccountAdapter):
    """Кастомний адаптер для обробки акаунтів"""
    
    def get_login_redirect_url(self, request):
        """
        Визначає URL для редіректу після входу
        """
        user = request.user
        if user.is_authenticated:
            if not user.phone_number:
                return '/accounts/register/step2/'
        
        return '/accounts/profile/'

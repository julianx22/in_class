from django.conf import settings
from django.shortcuts import resolve_url
from django.urls import reverse
from django.contrib.auth.views import LoginView
from .forms import EmailOrUsernameAuthenticationForm

class SmartLoginView(LoginView):
    template_name = 'registration/login.html'
    authentication_form = EmailOrUsernameAuthenticationForm

    def get_success_url(self):
        # respeta ?next=; si es staff/superuser, manda a /admin/
        redirect_to = self.get_redirect_url()
        user = self.request.user
        if user.is_authenticated and (user.is_staff or user.is_superuser):
            return reverse('admin:index')
        return redirect_to or resolve_url(settings.LOGIN_REDIRECT_URL)

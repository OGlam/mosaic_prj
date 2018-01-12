from django.contrib.auth.views import LoginView, PasswordResetView

from users.forms import MosaicLoginForm, MosaicPasswordResetForm


class MosaicLoginView(LoginView):
    form_class = MosaicLoginForm
    template_name = 'users/login.html'


class MosaicPasswordResetView(PasswordResetView):
    form_class = MosaicPasswordResetForm
    template_name = 'users/password_reset_form.html'

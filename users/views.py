from django.contrib.auth.views import LoginView, PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView

from mosaic_prj.base_views import IAAUIMixin
from users.forms import MosaicLoginForm, MosaicPasswordResetForm, ContactForm
from users.models import IAAContact
from django.utils.translation import ugettext_lazy as _


class MosaicLoginView(LoginView):
    form_class = MosaicLoginForm
    template_name = 'users/login.html'


class MosaicPasswordResetView(PasswordResetView):
    form_class = MosaicPasswordResetForm
    template_name = 'users/password_reset_form.html'


class ContactView(IAAUIMixin, SuccessMessageMixin, CreateView):
    template_name = 'users/contact_form.html'
    model = IAAContact
    success_url = reverse_lazy('contact')
    page_title = _('Contact us')
    page_name = 'contact_us'
    form_class = ContactForm
    success_message = _('Thank you, we will contact you shortly')

    def form_valid(self, form):
        form.send_email()
        return super().form_valid(form)

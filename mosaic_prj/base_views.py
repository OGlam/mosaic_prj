from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class IAAUIMixin(object):
    page_title = None
    page_name = None

    def get_page_title(self):
        if self.page_title:
            return self.page_title
        return ""

    def get_page_name(self):
        if self.page_name:
            return self.page_name
        return ""

    def is_msie(self):
        if settings.DEBUG:
            return True
        user_agent = self.request.META.get('HTTP_USER_AGENT', '')
        return 'MSIE' in user_agent or 'Trident' in user_agent

    def get_context_data(self, **kwargs):
        d = super(IAAUIMixin, self).get_context_data(**kwargs)
        d['page_title'] = self.get_page_title()
        d['page_name'] = self.get_page_name()
        return d


class LoginRequiredMixin(object):
    @method_decorator(login_required(login_url='login'))
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)

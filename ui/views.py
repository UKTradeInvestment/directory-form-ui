import json

from django.conf import settings
from django.shortcuts import redirect
from django.core.urlresolvers import reverse_lazy
from django.views.generic import TemplateView, FormView
from django.utils.cache import patch_response_headers
from django.template.response import TemplateResponse

from alice.helpers import rabbit
from ui.forms import CompanyFinder, ContactForm
from ui.helpers import search_companies


class CacheMixin(object):
    def render_to_response(self, context, **response_kwargs):
        # Get response from parent TemplateView class
        response = super().render_to_response(
            context, **response_kwargs
        )

        # Add Cache-Control and Expires headers
        patch_response_headers(response, cache_timeout=60 * 30)

        # Return response
        return response


class CachableTemplateView(CacheMixin, TemplateView):
    pass


class IndexView(CacheMixin, FormView):
    template_name = "index.html"
    form_class = ContactForm
    success_url = reverse_lazy("thanks")

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        json_data = {'data': json.dumps(form.cleaned_data)}
        response = rabbit.post(
            settings.DATA_SERVER + '/form/',
            data=json_data,
            request=self.request,
        )

        if not response.ok:
            return redirect("problem")

        return super().form_valid(form)


class CompanyFinder(FormView):
    template_name = "onboarding/company_finder.html"
    form_class = CompanyFinder

    def form_valid(self, form):
        results = search_companies(term=form.cleaned_data['term'])
        context = {'results': results}
        return TemplateResponse(self.request, self.template_name, context)

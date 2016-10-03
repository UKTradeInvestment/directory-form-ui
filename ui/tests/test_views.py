from unittest import mock
import http

from django.core.urlresolvers import reverse
from django.test import override_settings
import pytest

from ui.views import CompanyFinder, IndexView

VALID_REQUEST_DATA = {
    "contact_name": "Test",
    "marketing_source_bank": "",
    "website": "example.com",
    "exporting": "False",
    "phone_number": "",
    "marketing_source": "Social media",
    "opt_in": True,
    "marketing_s ource_other": "",
    "email_address1": "test@example.com",
    "agree_terms": True,
    "company_name": "Example Limited",
    "email_address2": "test@example.com"
}


@pytest.fixture
def search_results():
    return [{'label': 'company', 'id': 1}]


@pytest.fixture
def request_search_valid_bbc(rf):
    url = reverse('onboarding-find-company')
    return rf.post(url, {'term': 'BBC'})


@pytest.fixture
def request_search_invalid(rf):
    url = reverse('onboarding-find-company')
    return rf.post(url, {'terms': ''})


@override_settings(DATA_SERVER='test')
def test_index_view_create(rf):
    view = IndexView.as_view()
    request = rf.post('/', VALID_REQUEST_DATA)

    response_mock = mock.Mock(status_code=202, ok=True)
    with mock.patch('alice.helpers.rabbit.post', return_value=response_mock):
        response = view(request)

    assert response.url == reverse('thanks')


def test_company_finder_form_invalid_exposes_errors(request_search_invalid):
    view = CompanyFinder.as_view()
    response = view(request_search_invalid)
    assert response.status_code == http.client.OK
    assert 'term' in response.context_data['form'].errors


@mock.patch('ui.views.search_companies', return_value=[])
def test_company_finder_form_valid_exposes_results(
    mock_search_companies, search_results, request_search_valid_bbc
):
    mock_search_companies.return_value = search_results
    view = CompanyFinder.as_view()
    response = view(request_search_valid_bbc)
    assert response.status_code == http.client.OK
    assert response.context_data['results'] == search_results


@mock.patch('ui.views.search_companies')
def test_company_finder_passes_form_data_to_search(
    mock_search_companies, request_search_valid_bbc
):
    view = CompanyFinder.as_view()
    view(request_search_valid_bbc)
    assert mock_search_companies.called_with(term='BBC')

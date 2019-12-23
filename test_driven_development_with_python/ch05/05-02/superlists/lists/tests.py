import re

from django.urls import resolve
from django.test import TestCase
from django.http import HttpRequest
from django.template.loader import render_to_string

from lists.views import home_page


# 05-02 추가(2)
def remove_csrf(html_code):
    csrf_regex = r'<input[^>]+csrfmiddlewaretoken[^>]+>'
    return re.sub(csrf_regex, '', html_code)
# 05-02 추가(2)


class HomePageTest(TestCase):
    def test_root_url_resolves_to_home_page_view(self):
        found = resolve('/')
        self.assertEqual(found.func, home_page)

    def test_home_page_returns_correct_html(self):
        request = HttpRequest()
        response = home_page(request)
    # 05-02 추가(2)
        expected_html = render_to_string('home.html', request=request)
        self.assertEqual(remove_csrf(response.content.decode()), remove_csrf(expected_html))
    # 05-02 추가(2)

    # 05-02 추가(1)
    def test_home_page_can_save_a_POST_request(self):
        request = HttpRequest()
        request.method = 'POST'
        request.POST['item_text'] = '신규 작업 아이템'

        response = home_page(request)
        
        self.assertIn('신규 작업 아이템', response.content.decode())
    # 05-02 추가(1)

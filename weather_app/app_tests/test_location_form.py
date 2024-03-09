from django.test import TestCase, Client

# To fix "app not loaded" error when running pytest
# Pytest wasnt loading app settings correctly or something
import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'django_project.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_project.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

class TestLocationForm(TestCase):
    """
    Tests that zip code validation is working when passing weather
    location as a zip code in the home page sidebar form as query string
    ex : GET "/location=80918" on sidebar location submit 
    """
    def test_zip_code_validation(self):
      res = Client().get("/?location=80918")
      assert res.status_code == 200

    def test_zip_code_invalid(self):
      res = Client().get("/?location=0000000")
      # To follow rest compliance we return 206 which is partial content
      # in the case that location is invalid (since we still want the webpage to work)
      assert res.status_code == 206

    def test_zip_code_empty(self):
      res = Client().get("/")
      assert res.status_code == 200


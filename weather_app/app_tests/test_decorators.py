from django.test import TestCase, RequestFactory
from .. import decorators
from django.contrib.auth.models import User, Group
from django.urls import reverse
from weather_app.decorators import allowed_users
from django.http import HttpResponse


class TestDecorators(TestCase):
  def setUp(self):
    self.factory = RequestFactory()
    self.user = User.objects.create_user(username='testuser', email='123@example.com', password='test123123')
    self.admin_group = Group.objects.create(name='admin')
    self.normal_group = Group.objects.create(name='normal')

  def test_allowed_users_allowed(self):
    @allowed_users(allowed_roles=['admin'])
    def test_view(request):
      return HttpResponse('Allowed')

    self.user.groups.add(self.admin_group)
    request = self.factory.get(reverse('home'))
    request.user = self.user
    response = test_view(request)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.content.decode(), 'Allowed')
  
  def test_allowed_users_not_allowed(self):
    @allowed_users(allowed_roles=['admin'])
    def test_view(request):
      return HttpResponse('Allowed')

    self.user.groups.add(self.normal_group)
    request = self.factory.get(reverse('home'))
    request.user = self.user
    response = test_view(request)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.content.decode(), 'You are not allowed to access this page')
  
  def test_allowed_users_no_group(self):
    @allowed_users(allowed_roles=['admin'])
    def test_view(request):
      return HttpResponse('Allowed')

    request = self.factory.get(reverse('home'))
    request.user = self.user
    response = test_view(request)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.content.decode(), 'You are not allowed to access this page')



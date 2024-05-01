"""
Decorators for permissions of certain pages on the app. 
https://www.geeksforgeeks.org/creating-custom-decorator-in-django-for-different-permissions/
"""

from django.http import HttpResponse

#decorators
def allowed_users(allowed_roles=[]):
  """ Decorator that, when applied, only allows certain users. """
  def decorator(view_func):
    """ Decorator """
    def wrapper_func(request, *args, **kwargs):
      """ checks if user is allowed to access the page """
      print('role', allowed_roles)
      group = None
      if request.user.groups.exists():
        group = request.user.groups.all()[0].name
        print('group', group)
      if group in allowed_roles:
        return view_func(request, *args, **kwargs)
      return HttpResponse('You are not allowed to access this page')
    return wrapper_func
  return decorator

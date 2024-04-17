from django.http import HttpResponse
from django.shortcuts import redirect

#decorators
def allowed_users(allowed_roles=[]):
    def decorator(view_func):
      def wrapper_func(request, *args, **kwargs):
        print('role', allowed_roles)
        group = None
        if request.user.groups.exists():
          group = request.user.groups.all()[0].name
          print('group', group)
        if group in allowed_roles:
          return view_func(request, *args, **kwargs)
        else:
          return HttpResponse('You are not allowed to access this page')
      return wrapper_func
    return decorator

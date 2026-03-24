from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache

@never_cache
def index(request):
    if request.user.is_authenticated:
        auth_logout(request)
    return render(request,'homepage.html')


@never_cache
def portal_entry(request, destination):
    destination_map = {
        'student-login': 'login',
        'student-register': 'register',
        'faculty-login': 'faculty-login',
        'faculty-register': 'faculty-register',
    }
    route_name = destination_map.get(destination)
    if route_name is None:
        return redirect('homepage')

    if request.user.is_authenticated:
        auth_logout(request)

    return redirect(route_name)

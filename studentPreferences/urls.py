from django.urls import path
from . import views
urlpatterns = [
    path('',views.index,name = "email-student-pref"),
    path('change-password/',views.change_password,name="change_password"),
    path('support/', views.contact_support, name='contact_support'),
    path('email-change-request/', views.request_email_change, name='request_email_change'),
]

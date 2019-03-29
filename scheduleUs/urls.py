"""scheduleUs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView
from scheduleUs import views

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('about/', TemplateView.as_view(template_name='about.html'), name="about"),
    path('contact/', TemplateView.as_view(template_name='contact.html'), name="contact"),
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('users/', include('django.contrib.auth.urls')),
    path('create_event/', views.create_event, name='create_event'),
    path('dashboard/', views.dashboard, name = 'dashboard'),
    path('<int:event_id>/', views.event_page, name = 'event_page'),
    path('delete_event/', views.delete_event, name = 'delete_event'),
    path('<int:pk>/delete/', views.EventDelete.as_view(), name='event_confirm_delete'),
    path('<int:pk>/event_update/', views.EventUpdate.as_view(), name='event_update'),
]

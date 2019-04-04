from django.urls import path
from . import views
from django.views.generic.base import TemplateView

urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('dashboard/', TemplateView.as_view(template_name='dashboard.html'), name="dashboard"),
    path('add_friend/', views.add_friend, name='add_friend')
]

from django.urls import path

from fronts import views

urlpatterns = [
    path('homepage/', views.HomepageFormView.as_view(), name='homepage_form'),
    ]
from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy

app_name = 'account'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.user_profile, name='user_profile'),
    path('logout/', LogoutView.as_view(next_page=reverse_lazy('home:index')), name='logout'),
]

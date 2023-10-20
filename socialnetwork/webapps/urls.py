"""
URL configuration for webapps project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from socialnetwork import views

urlpatterns = [
    path('', views.global_stream),
    path('login', views.login_action, name='login'),
    path('register', views.register_action, name='register'),
    path('global_stream', views.global_stream, name='global_stream'),
    path('follower_stream', views.follower_stream, name='follower_stream'),
    path('profile', views.profile, name='profile'),
    path('logout', views.logout_action, name='logout'),
    path('other_profile/<int:id>', views.other_profile, name='other_profile'),
    path('unfollow/<int:id>', views.unfollow, name='unfollow'),
    path('follow/<int:id>', views.follow, name='follow'),
    path('photo/<int:id>', views.get_photo, name='photo'),
    path('socialnetwork/get-global', views.get_global, name='get-global'),
    path('socialnetwork/get-follower', views.get_follower, name='get-follower'),
    path('socialnetwork/add-comment', views.add_comment, name='add-comment'),
]

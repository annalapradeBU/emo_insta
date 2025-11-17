# File: urls.py
# Author: Anna LaPrade (alaprade@bu.edu), 09/23/2025
# Description: the url patterns for the mini_insta

from django.urls import path
from .views import *

# generic view for authentication/authorization
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('',  ShowAllView.as_view(), name="show_all_profiles"),
    path('profile/<int:pk>', ProfileDetailView.as_view(), name='show_profile'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='show_post'),
    path('profile/create_post', CreatePostView.as_view(), name='create_post'),
    path('profile/update', UpdateProfileView.as_view(), name='update_profile'),
    path('post/<int:pk>/delete', DeletePostView.as_view(), name='delete_post'),
    path('post/<int:pk>/update', UpdatePostView.as_view(), name='update_post'),
    path('profile/<int:pk>/followers', ShowFollowersDetailView.as_view(), name='show_followers'),
    path('profile/<int:pk>/following', ShowFollowingDetailView.as_view(), name='show_following'),
    path('profile/feed', PostFeedListView.as_view(), name="show_feed"),
    path('profile/search', SearchView.as_view(), name='search'),

    # authorization-realted URLS:
    path('login/', auth_views.LoginView.as_view(template_name='mini_insta/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view( template_name='mini_insta/logout.html'), name='logout'),
    path('create_profile/', CreateProfileView.as_view(), name='create_profile'),
    path('profile/<int:pk>/follow', FollowView.as_view(), name='follow'),
    path('profile/<int:pk>/delete_follow', DeleteFollowView.as_view(), name='delete_follow'),
    path('post/<int:pk>/like', LikeView.as_view(), name='like'),
    path('post/<int:pk>/delete_like', DeleteLikeView.as_view(), name='delete_like'),
    path('post/<int:pk>/comment/', CreateCommentView.as_view(), name='create_comment'),
    path('comment/<int:pk>/delete/', DeleteCommentView.as_view(), name='delete_comment'),
]
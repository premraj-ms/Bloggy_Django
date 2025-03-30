from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.web_index, name="index"),
    path('draft/', views.web_blogdraft, name="web_blogdraft"),
    path('category/<str:catSlug>/', views.web_category, {'page': 1}, name='web_category'),
    path('category/<catSlug>/<int:page>/', views.web_category, name="web_category_paginated"),

    path('search/', views.web_search, name="web_search"),
    path('profile/', views.web_userprofile, name="web_userprofile"),
    path('post/delete/<int:delno>', views.delete_post, name='delete_post'),
    path('login/', views.web_login, name="web_login"),
    path('signup/', views.web_register, name="web_register"),
    path('signup/email-validation/<se_id>', views.web_uservalidation, name="web_uservalidation"),
    path('web_reg_user/', views.web_reg_user, name="register_users"),
    path('web_log_user/', views.web_log_user, name="web_log_user"),
    path("web_logout_user/", views.web_logout_user, name="web_logout_user"),
    path("profile/edit/", views.web_user_edit, name="web_user_edit"),
    path("profile/edit/save",views.user_save_user_details, name="user_save_user_details"),
    
    
    path('google/login/', views.google_login, name='google_login'),
    path('google/callback/', views.google_callback, name='google_callback'),
    
    path('profile/media-files/', views.media_files, name='media_files'),
    path('profile/media-files/save', views.media_file_save, name='media_file_save'),
    
    path('profile/media-files/delete/<int:del_id>/', views.delete_media_files, name='delete_media_files'),
    path('profile/media-files/json', views.media_image_list_json, name='media_image_list_json'),
    
    path('profile/media-files/ajax_images', views.ajax_images, name='ajax_images'),
    
    path('draft/save/1', views.post_save, name='post_save'),
    path('draft/<int:post_id>', views.update_post, name='update_post'),
    
    path('draft/post_update_now/<int:post_id>', views.post_update_now, name="post_update_now"),
    
    path('user/<user_slug>', views.users, name="user_page"),
    path('live-search/', views.live_search, name='live_search'),
    path('follow-toggle/<int:user_id>/', views.FollowToggleView.as_view(), name='follow_toggle'),
    path("deletecomment/<int:cid>/", views.deletecomment, name="deletecomment"),
    path('fetch-notifications/', views.fetch_notifications, name='fetch-notifications'),
    
    path('following/',views.followers, name='following'),
    
    path('comments_save/<int:post_id>', views.comments_save, name='comments_save'),
    path('<slug:category>/<slug:post>/', views.web_post, name="web_post"),
    
]

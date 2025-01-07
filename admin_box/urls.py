from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('login/', views.ad_login, name="ad_login"),
    path('category/', views.ad_category, name="ad_category"),
    path('add-category/', views.ad_add_category, name="ad_add_category"),
    
    
    
    path('save_category/', views.save_category, name="save_category"),
    path('delete_category/<int:del_id>', views.cat_delete, name='cat_delete'),
    path('edit_category/<int:edit_id>', views.ad_edit_categories, name='cat_edit'),
    path('update_category/', views.update_category, name='cat_update'),
    
    
    
]
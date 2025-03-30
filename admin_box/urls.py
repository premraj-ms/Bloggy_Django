from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index.admin"),
    path('login/', views.ad_login, name="ad_login"),
    path('category/', views.ad_category, name="ad_category"),
    path('add-category/', views.ad_add_category, name="ad_add_category"),
    
    path('user-list', views.userList, name="userList"),
    path('comment-list', views.commentList, name="commmentList"),
    path('blogpost-list', views.BlogpostList, name="blogpostList"),
    
    path('save_category/', views.save_category, name="save_category"),
    path('delete_category/<int:del_id>', views.cat_delete, name='cat_delete'),
    path('edit_category/<int:edit_id>', views.ad_edit_categories, name='cat_edit'),
    path('update_category/', views.update_category, name='cat_update'),
    
    path('delete/user/<int:delId>', views.delUser, name='delUser'),
    path('delete/comment/<int:delId>', views.delComment, name='delComment'),
    path('delete/post/<int:delId>', views.delPost, name='delPost'),
    
    
    
]
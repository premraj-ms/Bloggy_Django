from django.db import models
from django.contrib.auth.hashers import make_password, is_password_usable
from django.utils.text import slugify
import random

from admin_box.models import Categories

class Web_users(models.Model):
    user_name = models.SlugField(max_length=100, unique=True)
    full_name = models.CharField(max_length=60, null=False, blank=False)
    user_email = models.EmailField(max_length=260, null=False, blank=False, unique=True)
    user_bio = models.CharField(max_length=190, null=True, blank=True)
    user_profile_image = models.ImageField(
        upload_to="user_Profile_image", 
        default="user_Profile_image/default.png"
    )
    user_about = models.CharField(max_length=500, null=True, blank=True)
    user_skills = models.CharField(max_length=300, null=True, blank=True)
    user_password = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    verified = models.BooleanField(default=False)
    
   
class Web_post(models.Model):
    post_title = models.CharField(max_length=80, blank=True, default="untitled")
    post_author = models.ForeignKey(Web_users, on_delete=models.CASCADE, related_name="posts")
    post_category = models.ForeignKey(Categories, on_delete=models.CASCADE, related_name="posts")
    post_desc = models.CharField(max_length=250, null=True, blank=True)
    post_cover = models.ImageField(upload_to="Post_cover")
    post_content = models.TextField()
    post_published = models.BooleanField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    view_count = models.IntegerField(default=0)
    post_slug = models.SlugField(max_length=100, unique=True)

class Follow(models.Model):
    user = models.ForeignKey(Web_users, on_delete=models.CASCADE, related_name='following')
    following_user = models.ForeignKey(Web_users, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

class Post_image(models.Model):
    image_url = models.ImageField(upload_to="Post_Images" )
    image_by = models.IntegerField( blank=False)
    

class Comment(models.Model):
    post = models.ForeignKey(Web_post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(Web_users, on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)
    
    def __str__(self):
        return self.id

class Notification(models.Model):
    user = models.ForeignKey(Web_users, on_delete=models.CASCADE, related_name='notifications')
    post_by = models.ForeignKey(Web_users, on_delete=models.CASCADE, related_name='posted_notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    